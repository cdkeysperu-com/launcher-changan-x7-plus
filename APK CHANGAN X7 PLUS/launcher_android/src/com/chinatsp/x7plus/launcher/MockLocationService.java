package com.chinatsp.x7plus.launcher;

import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.location.Criteria;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.Build;
import android.os.Bundle;
import android.os.IBinder;
import android.os.SystemClock;
import android.util.Log;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.HttpURLConnection;
import java.net.InetSocketAddress;
import java.net.URL;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Subsistema Híbrido de Localización Satelital para Changan X7 Plus.
 * 
 * Hardware: MediaTek MT8666 / Android 9 (API 28).
 * 
 * Modos de Operación:
 * 1. MODE_NATIVE_GPS = 0 (PREDETERMINADO):
 *    - Limpia y remueve cualquier TestProvider / Mock Location.
 *    - Permite que el chip GNSS / GPS físico del vehículo entregue coordenadas satelitales
 *      directas y continuas a Waze, Google Maps y al sistema Android.
 *    - Escucha la ubicación nativa para alimentar el velocímetro y widgets del launcher.
 * 
 * 2. MODE_MOCK_TETHER = 1:
 *    - Inyecta telemetría satelital compartida desde un teléfono móvil vía socket UDP 10110
 *      o respaldo de red.
 *    - Incluye hilo de keepalive de 1 Hz con elapsedRealtimeNanos() para evitar que Waze
 *      indique "Sin señal de GPS".
 */
public class MockLocationService extends Service {

    private static final String TAG = "MockLocationService";
    private static final String PREFS_GPS = "Changan_Gps_Prefs";
    public static final String KEY_GPS_MODE = "gps_operating_mode"; // 0 = Nativo Auto, 1 = Mock Móvil
    private static final String KEY_LAT = "last_valid_lat";
    private static final String KEY_LON = "last_valid_lon";
    private static final String KEY_BEARING = "last_valid_bearing";
    public static final int UDP_PORT = 10110;

    public static final int MODE_NATIVE_GPS = 0;
    public static final int MODE_MOCK_TETHER = 1;

    private static MockLocationService sInstance;
    private LocationManager locationManager;
    private SharedPreferences gpsPrefs;
    private volatile boolean isRunning = false;
    private Thread udpListenerThread;
    private Thread keepaliveHeartbeatThread;

    public interface OnLocationUpdateListener {
        void onLocationUpdated(double lat, double lon, double speed, double bearing, float accuracy);
    }

    private static OnLocationUpdateListener sListener;
    private static volatile boolean sUdpPacketReceived = false;
    private static float sLastValidBearing = 0.0f;

    private static double sLastLat = -12.0125;  // Default de referencia: Callao / Pacasmayo, Lima
    private static double sLastLon = -77.1080;
    private static double sLastAlt = 35.0;
    private static double sLastSpeed = 0.0;
    private static double sLastBearing = 0.0;
    private static float sLastAccuracy = 3.0f;
    private static long sLastUpdateTime = 0;
    private static int sCurrentMode = MODE_NATIVE_GPS;

    public static void setLocationUpdateListener(OnLocationUpdateListener listener) {
        sListener = listener;
        if (sListener != null && sLastUpdateTime > 0) {
            sListener.onLocationUpdated(sLastLat, sLastLon, sLastSpeed, sLastBearing, sLastAccuracy);
        }
    }

    public static int getGpsMode(Context ctx) {
        if (ctx == null) return sCurrentMode;
        SharedPreferences p = ctx.getSharedPreferences(PREFS_GPS, MODE_PRIVATE);
        sCurrentMode = p.getInt(KEY_GPS_MODE, MODE_NATIVE_GPS);
        return sCurrentMode;
    }

    public static void setGpsMode(Context ctx, int mode) {
        sCurrentMode = mode;
        if (ctx != null) {
            ctx.getSharedPreferences(PREFS_GPS, MODE_PRIVATE)
                .edit()
                .putInt(KEY_GPS_MODE, mode)
                .apply();
        }
        if (sInstance != null) {
            sInstance.applyOperatingMode(mode);
        }
    }

    public static void restoreNativeHardwareGps(Context ctx) {
        setGpsMode(ctx, MODE_NATIVE_GPS);
    }

    public static boolean isGpsActive() {
        return (System.currentTimeMillis() - sLastUpdateTime) < 20000 && sLastLat != 0.0;
    }

    public static double getLastLat() { return sLastLat; }
    public static double getLastLon() { return sLastLon; }
    public static double getLastSpeed() { return sLastSpeed; }
    public static double getLastBearing() { return sLastBearing; }
    public static float getLastAccuracy() { return sLastAccuracy; }
    public static long getLastUpdateTime() { return sLastUpdateTime; }

    @Override
    public void onCreate() {
        super.onCreate();
        sInstance = this;
        locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
        gpsPrefs = getSharedPreferences(PREFS_GPS, MODE_PRIVATE);

        // Restaurar última posición guardada
        sLastLat = Double.longBitsToDouble(gpsPrefs.getLong(KEY_LAT, Double.doubleToLongBits(-12.0125)));
        sLastLon = Double.longBitsToDouble(gpsPrefs.getLong(KEY_LON, Double.doubleToLongBits(-77.1080)));
        sLastValidBearing = gpsPrefs.getFloat(KEY_BEARING, 0.0f);
        sLastBearing = sLastValidBearing;

        sCurrentMode = gpsPrefs.getInt(KEY_GPS_MODE, MODE_NATIVE_GPS);
        isRunning = true;

        applyOperatingMode(sCurrentMode);
    }

    private void applyOperatingMode(int mode) {
        Log.i(TAG, "Aplicando modo de operación GPS: " + (mode == MODE_NATIVE_GPS ? "NATIVO HARDWARE" : "MOCK TETHER"));

        if (mode == MODE_NATIVE_GPS) {
            // 1. Deshabilitar y desregistrar cualquier TestProvider para desbloquear el GPS físico
            removeMockProviders();
            // 2. Registrar escucha directa al chip GPS del auto
            registerNativeLocationListeners();
        } else {
            // MODO MOCK TETHER: Inyección de datos desde celular
            unregisterNativeLocationListeners();
            initMockProviders();
            startUdpGpsListener();
            startKeepaliveHeartbeat();
            startIpFallbackCountdown();

            // Inyección inicial con posición guardada
            injectLocation(sLastLat, sLastLon, 0.0f, sLastValidBearing, 10.0f, sLastAlt);
        }
    }

    // ========================================================================
    // A. MODO NATIVO (GPS FÍSICO DEL CHANGAN X7 PLUS)
    // ========================================================================

    private final LocationListener nativeGpsListener = new LocationListener() {
        @Override
        public void onLocationChanged(Location location) {
            if (location == null) return;
            handleNativeLocationUpdate(location);
        }

        @Override
        public void onStatusChanged(String provider, int status, Bundle extras) {}

        @Override
        public void onProviderEnabled(String provider) {
            Log.i(TAG, "Proveedor nativo habilitado: " + provider);
        }

        @Override
        public void onProviderDisabled(String provider) {
            Log.w(TAG, "Proveedor nativo deshabilitado: " + provider);
        }
    };

    private void registerNativeLocationListeners() {
        if (locationManager == null) return;
        try {
            // Solicitar actualizaciones del sensor físico GNSS
            if (locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
                locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1000L, 1.0f, nativeGpsListener);
                Log.i(TAG, "Escuchador de GPS físico registrado con éxito.");
            }
        } catch (SecurityException se) {
            Log.w(TAG, "Permiso de ubicación denegado para GPS nativo: " + se.getMessage());
        } catch (Exception e) {
            Log.w(TAG, "Excepción registrando GPS nativo: " + e.getMessage());
        }

        try {
            if (locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)) {
                locationManager.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 3000L, 5.0f, nativeGpsListener);
            }
        } catch (Exception ignored) {}

        // Intentar obtener última ubicación conocida para arranque rápido
        try {
            Location lastGps = locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER);
            if (lastGps != null) {
                handleNativeLocationUpdate(lastGps);
            }
        } catch (Exception ignored) {}
    }

    private void unregisterNativeLocationListeners() {
        if (locationManager != null && nativeGpsListener != null) {
            try {
                locationManager.removeUpdates(nativeGpsListener);
            } catch (Exception ignored) {}
        }
    }

    private void handleNativeLocationUpdate(Location loc) {
        sLastLat = loc.getLatitude();
        sLastLon = loc.getLongitude();
        sLastAlt = loc.hasAltitude() ? loc.getAltitude() : sLastAlt;
        sLastSpeed = loc.hasSpeed() ? (loc.getSpeed() * 3.6) : 0.0;
        if (loc.hasBearing() && loc.getBearing() > 0.0f) {
            sLastValidBearing = loc.getBearing();
        }
        sLastBearing = sLastValidBearing;
        sLastAccuracy = loc.hasAccuracy() ? loc.getAccuracy() : 5.0f;
        sLastUpdateTime = System.currentTimeMillis();

        // Persistir coordenadas en SharedPreferences
        if (gpsPrefs != null) {
            gpsPrefs.edit()
                .putLong(KEY_LAT, Double.doubleToLongBits(sLastLat))
                .putLong(KEY_LON, Double.doubleToLongBits(sLastLon))
                .putFloat(KEY_BEARING, sLastValidBearing)
                .apply();
        }

        // Notificar a la interfaz de usuario del Launcher
        if (sListener != null) {
            sListener.onLocationUpdated(sLastLat, sLastLon, sLastSpeed, sLastBearing, sLastAccuracy);
        }
    }

    // ========================================================================
    // B. GESTIÓN DE TEST PROVIDERS (MODO MOCK TETHER)
    // ========================================================================

    private void removeMockProviders() {
        if (locationManager == null) return;
        try {
            locationManager.setTestProviderEnabled(LocationManager.GPS_PROVIDER, false);
            locationManager.removeTestProvider(LocationManager.GPS_PROVIDER);
            Log.i(TAG, "TestProvider GPS_PROVIDER removido exitosamente.");
        } catch (Exception ignored) {}

        try {
            locationManager.setTestProviderEnabled(LocationManager.NETWORK_PROVIDER, false);
            locationManager.removeTestProvider(LocationManager.NETWORK_PROVIDER);
            Log.i(TAG, "TestProvider NETWORK_PROVIDER removido exitosamente.");
        } catch (Exception ignored) {}
    }

    private void initMockProviders() {
        if (locationManager == null) return;
        setupProvider(LocationManager.GPS_PROVIDER);
        setupProvider(LocationManager.NETWORK_PROVIDER);
    }

    private void setupProvider(String providerName) {
        if (locationManager == null) return;
        try {
            locationManager.addTestProvider(
                providerName,
                false, false, false, false,
                true, true, true,
                Criteria.POWER_LOW,
                Criteria.ACCURACY_FINE
            );
        } catch (SecurityException se) {
            Log.w(TAG, "Permiso Mock Location aún no activado para: " + providerName + " (" + se.getMessage() + ")");
            return;
        } catch (IllegalArgumentException iae) {
            // El proveedor ya existe en el LocationManager
        } catch (Exception ignored) {}

        try {
            locationManager.setTestProviderEnabled(providerName, true);
            Log.i(TAG, "TestProvider habilitado con éxito: " + providerName);
        } catch (Exception ignored) {}
    }

    /**
     * Hilo Heartbeat de 1 Hz para Waze en modo Mock:
     * Si no llegan paquetes por 1-2 segundos, repite la última coordenada válida
     * con elapsedRealtimeNanos() fresco para que Waze no declare pérdida de satélite.
     */
    private void startKeepaliveHeartbeat() {
        if (keepaliveHeartbeatThread != null && keepaliveHeartbeatThread.isAlive()) return;

        keepaliveHeartbeatThread = new Thread(new Runnable() {
            @Override
            public void run() {
                while (isRunning && sCurrentMode == MODE_MOCK_TETHER) {
                    try {
                        Thread.sleep(1000);
                        if (sCurrentMode != MODE_MOCK_TETHER) break;

                        // Reinyectar cada 1 segundo para mantener activo Waze
                        if (sLastLat != 0.0 && sLastLon != 0.0) {
                            injectLocation(sLastLat, sLastLon, (float) (sLastSpeed / 3.6), (float) sLastBearing, sLastAccuracy, sLastAlt);
                        }
                    } catch (InterruptedException ignored) {
                        break;
                    } catch (Exception ignored) {}
                }
            }
        }, "ChanganGpsHeartbeat");
        keepaliveHeartbeatThread.start();
    }

    /**
     * Inyección a LocationManager para aplicaciones en modo Mock.
     */
    public synchronized void injectLocation(double lat, double lon, float speedMs, float bearing, float acc, double alt) {
        if (sCurrentMode != MODE_MOCK_TETHER) return;
        if (lat == 0.0 && lon == 0.0) return;

        float effectiveBearing;
        if (speedMs < 0.8f || bearing <= 0.0f) {
            effectiveBearing = sLastValidBearing;
        } else {
            sLastValidBearing = bearing;
            effectiveBearing = bearing;
        }

        float effectiveAccuracy = acc > 0.0f ? acc : 3.0f;

        sLastLat = lat;
        sLastLon = lon;
        sLastAlt = alt;
        sLastSpeed = speedMs * 3.6;
        sLastBearing = effectiveBearing;
        sLastAccuracy = effectiveAccuracy;
        sLastUpdateTime = System.currentTimeMillis();

        if (gpsPrefs != null) {
            gpsPrefs.edit()
                .putLong(KEY_LAT, Double.doubleToLongBits(lat))
                .putLong(KEY_LON, Double.doubleToLongBits(lon))
                .putFloat(KEY_BEARING, effectiveBearing)
                .apply();
        }

        if (sListener != null) {
            sListener.onLocationUpdated(sLastLat, sLastLon, sLastSpeed, sLastBearing, sLastAccuracy);
        }

        if (locationManager == null) return;

        long nowTime = System.currentTimeMillis();
        long nowNanos = SystemClock.elapsedRealtimeNanos();

        // Inyección a GPS_PROVIDER (Waze, Magic Earth, Google Maps)
        try {
            Location locGps = new Location(LocationManager.GPS_PROVIDER);
            locGps.setLatitude(lat);
            locGps.setLongitude(lon);
            locGps.setAltitude(alt);
            locGps.setSpeed(speedMs);
            locGps.setBearing(effectiveBearing);
            locGps.setAccuracy(effectiveAccuracy);
            locGps.setTime(nowTime);
            locGps.setElapsedRealtimeNanos(nowNanos);

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                locGps.setSpeedAccuracyMetersPerSecond(0.5f);
                locGps.setBearingAccuracyDegrees(5.0f);
                locGps.setVerticalAccuracyMeters(2.0f);
            }

            locationManager.setTestProviderLocation(LocationManager.GPS_PROVIDER, locGps);
        } catch (Exception e) {
            setupProvider(LocationManager.GPS_PROVIDER);
        }

        // Inyección a NETWORK_PROVIDER
        try {
            Location locNet = new Location(LocationManager.NETWORK_PROVIDER);
            locNet.setLatitude(lat);
            locNet.setLongitude(lon);
            locNet.setAltitude(alt);
            locNet.setSpeed(speedMs);
            locNet.setBearing(effectiveBearing);
            locNet.setAccuracy(effectiveAccuracy);
            locNet.setTime(nowTime);
            locNet.setElapsedRealtimeNanos(nowNanos);

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                locNet.setSpeedAccuracyMetersPerSecond(0.5f);
                locNet.setBearingAccuracyDegrees(5.0f);
                locNet.setVerticalAccuracyMeters(2.0f);
            }

            locationManager.setTestProviderLocation(LocationManager.NETWORK_PROVIDER, locNet);
        } catch (Exception ignored) {}
    }

    public synchronized void injectLocation(double lat, double lon, double speedMs, double bearing, float acc) {
        injectLocation(lat, lon, (float) speedMs, (float) bearing, acc, sLastAlt);
    }

    // ========================================================================
    // C. SOCKET UDP 10110 (MÓVIL COMPARTIDO)
    // ========================================================================

    private void startUdpGpsListener() {
        if (udpListenerThread != null && udpListenerThread.isAlive()) return;

        udpListenerThread = new Thread(new Runnable() {
            @Override
            public void run() {
                byte[] buffer = new byte[2048];
                while (isRunning && sCurrentMode == MODE_MOCK_TETHER) {
                    DatagramSocket socket = null;
                    try {
                        socket = new DatagramSocket(null);
                        socket.setReuseAddress(true);
                        socket.bind(new InetSocketAddress(UDP_PORT));
                        socket.setBroadcast(true);
                        Log.i(TAG, "Socket UDP en puerto " + UDP_PORT + " vinculado exitosamente.");

                        while (isRunning && sCurrentMode == MODE_MOCK_TETHER) {
                            DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                            socket.receive(packet);
                            String data = new String(packet.getData(), 0, packet.getLength(), "UTF-8").trim();
                            if (!data.isEmpty()) {
                                sUdpPacketReceived = true;
                                processIncomingTelemetry(data);
                            }
                        }
                    } catch (Exception e) {
                        try { Thread.sleep(2000); } catch (InterruptedException ignored) {}
                    } finally {
                        if (socket != null && !socket.isClosed()) {
                            try { socket.close(); } catch (Exception ignored) {}
                        }
                    }
                }
            }
        }, "ChanganUdpGpsThread");
        udpListenerThread.start();
    }

    private void processIncomingTelemetry(String rawData) {
        if (rawData == null || rawData.isEmpty()) return;
        String[] lines = rawData.split("\r?\n");
        for (String line : lines) {
            line = line.trim();
            if (line.isEmpty()) continue;

            if (line.startsWith("{")) {
                parseJsonGps(line);
            } else if (line.startsWith("$")) {
                parseNmeaSentence(line);
            } else if (line.contains(",")) {
                parseCsvGps(line);
            }
        }
    }

    private void parseJsonGps(String jsonStr) {
        try {
            JSONObject obj = new JSONObject(jsonStr);
            double lat = obj.has("lat") ? obj.getDouble("lat") : (obj.has("latitude") ? obj.getDouble("latitude") : 0.0);
            double lon = obj.has("lon") ? obj.getDouble("lon") : (obj.has("lng") ? obj.getDouble("lng") : (obj.has("longitude") ? obj.getDouble("longitude") : 0.0));
            float speed = (float) (obj.has("speed") ? obj.getDouble("speed") : 0.0);
            float bearing = (float) (obj.has("bearing") ? obj.getDouble("bearing") : (obj.has("heading") ? obj.getDouble("heading") : 0.0));
            float acc = (float) (obj.has("acc") ? obj.getDouble("acc") : (obj.has("accuracy") ? obj.getDouble("accuracy") : 3.0f));
            double alt = obj.has("alt") ? obj.getDouble("alt") : (obj.has("altitude") ? obj.getDouble("altitude") : sLastAlt);

            if (lat != 0.0 && lon != 0.0) {
                injectLocation(lat, lon, speed, bearing, acc, alt);
            }
        } catch (Exception e) {
            parseJsonRegexFallback(jsonStr);
        }
    }

    private void parseJsonRegexFallback(String json) {
        try {
            double lat = extractJsonDouble(json, "lat");
            double lon = extractJsonDouble(json, "lon");
            if (lon == 0.0) lon = extractJsonDouble(json, "lng");
            float speed = (float) extractJsonDouble(json, "speed");
            float bearing = (float) extractJsonDouble(json, "bearing");
            float acc = (float) extractJsonDouble(json, "acc");
            if (acc <= 0.0f) acc = 3.0f;
            double alt = extractJsonDouble(json, "alt");
            if (alt == 0.0) alt = sLastAlt;

            if (lat != 0.0 && lon != 0.0) {
                injectLocation(lat, lon, speed, bearing, acc, alt);
            }
        } catch (Exception ignored) {}
    }

    private double extractJsonDouble(String json, String key) {
        Pattern pattern = Pattern.compile("\"" + key + "\"\\s*:\\s*([\\-0-9\\.]+)");
        Matcher matcher = pattern.matcher(json);
        if (matcher.find()) {
            return Double.parseDouble(matcher.group(1));
        }
        return 0.0;
    }

    private void parseNmeaSentence(String sentence) {
        try {
            if (sentence.startsWith("$GPRMC") || sentence.startsWith("$GNRMC") || sentence.contains("RMC,")) {
                parseNmeaRmc(sentence);
            } else if (sentence.startsWith("$GPGGA") || sentence.startsWith("$GNGGA") || sentence.contains("GGA,")) {
                parseNmeaGga(sentence);
            }
        } catch (Exception ignored) {}
    }

    private void parseNmeaRmc(String rmc) {
        String[] tokens = rmc.split(",");
        if (tokens.length >= 7) {
            String status = tokens[2].trim();
            if ("A".equalsIgnoreCase(status)) {
                double lat = convertNmeaToDecimal(tokens[3], tokens[4]);
                double lon = convertNmeaToDecimal(tokens[5], tokens[6]);
                float speedKnots = (tokens.length > 7 && !tokens[7].isEmpty()) ? (float) Double.parseDouble(tokens[7]) : 0.0f;
                float speedMs = speedKnots * 0.514444f;
                float bearing = (tokens.length > 8 && !tokens[8].isEmpty()) ? (float) Double.parseDouble(tokens[8]) : 0.0f;

                injectLocation(lat, lon, speedMs, bearing, 3.0f, sLastAlt);
            }
        }
    }

    private void parseNmeaGga(String gga) {
        String[] tokens = gga.split(",");
        if (tokens.length >= 10) {
            String quality = tokens[6].trim();
            if (!"0".equals(quality) && !quality.isEmpty()) {
                double lat = convertNmeaToDecimal(tokens[2], tokens[3]);
                double lon = convertNmeaToDecimal(tokens[4], tokens[5]);
                float hdop = (!tokens[8].isEmpty()) ? (float) Double.parseDouble(tokens[8]) : 1.2f;
                float acc = Math.max(2.0f, Math.min(15.0f, hdop * 2.5f));
                double alt = (!tokens[9].isEmpty()) ? Double.parseDouble(tokens[9]) : sLastAlt;

                injectLocation(lat, lon, (float) (sLastSpeed / 3.6), (float) sLastBearing, acc, alt);
            }
        }
    }

    private double convertNmeaToDecimal(String coord, String dir) {
        if (coord == null || coord.isEmpty()) return 0.0;
        double raw = Double.parseDouble(coord);
        int degrees = (int) (raw / 100.0);
        double minutes = raw - (degrees * 100.0);
        double decimal = degrees + (minutes / 60.0);
        if ("S".equalsIgnoreCase(dir) || "W".equalsIgnoreCase(dir)) {
            decimal = -decimal;
        }
        return decimal;
    }

    private void parseCsvGps(String csv) {
        try {
            String[] parts = csv.split(",");
            if (parts.length >= 2) {
                double lat = Double.parseDouble(parts[0].trim());
                double lon = Double.parseDouble(parts[1].trim());
                float speed = parts.length > 2 ? (float) Double.parseDouble(parts[2].trim()) : 0.0f;
                float bearing = parts.length > 3 ? (float) Double.parseDouble(parts[3].trim()) : 0.0f;
                float acc = parts.length > 4 ? (float) Double.parseDouble(parts[4].trim()) : 3.0f;
                double alt = parts.length > 5 ? Double.parseDouble(parts[5].trim()) : sLastAlt;
                injectLocation(lat, lon, speed, bearing, acc, alt);
            }
        } catch (Exception ignored) {}
    }

    private void startIpFallbackCountdown() {
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    Thread.sleep(8000);
                    if (!sUdpPacketReceived && isRunning && sCurrentMode == MODE_MOCK_TETHER && isWifiConnected()) {
                        fetchIpGeolocation();
                    }
                } catch (InterruptedException ignored) {}
            }
        }, "ChanganIpFallbackThread").start();
    }

    private boolean isWifiConnected() {
        try {
            ConnectivityManager cm = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
            if (cm != null) {
                NetworkInfo ni = cm.getNetworkInfo(ConnectivityManager.TYPE_WIFI);
                return ni != null && ni.isConnected();
            }
        } catch (Exception ignored) {}
        return false;
    }

    private void fetchIpGeolocation() {
        if (sUdpPacketReceived) return;

        try {
            URL url = new URL("http://ip-api.com/json/?fields=lat,lon,city,country");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setConnectTimeout(4000);
            conn.setReadTimeout(4000);
            if (conn.getResponseCode() == 200) {
                BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                StringBuilder sb = new StringBuilder();
                String line;
                while ((line = br.readLine()) != null) sb.append(line);
                br.close();

                if (sUdpPacketReceived || sCurrentMode != MODE_MOCK_TETHER) return;

                JSONObject json = new JSONObject(sb.toString());
                if (json.has("lat") && json.has("lon")) {
                    double lat = json.getDouble("lat");
                    double lon = json.getDouble("lon");
                    if (!sUdpPacketReceived && lat != 0.0 && lon != 0.0) {
                        injectLocation(lat, lon, 0.0f, sLastValidBearing, 35.0f, 35.0);
                    }
                }
            }
        } catch (Exception ignored) {}
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && intent.hasExtra("SET_GPS_MODE")) {
            int newMode = intent.getIntExtra("SET_GPS_MODE", MODE_NATIVE_GPS);
            setGpsMode(this, newMode);
        }
        return START_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onDestroy() {
        isRunning = false;
        unregisterNativeLocationListeners();
        removeMockProviders();
        sInstance = null;
        super.onDestroy();
    }
}
