package com.chinatsp.x7plus.launcher;

import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.util.Log;

public class HardwareKeyReceiver extends BroadcastReceiver {

    private static final String TAG = "HardwareKeyReceiver";
    private static final String PREFS_NAME = "CockpitX7Prefs";
    private static final String KEY_CAM_PKG = "pref_camera_pkg";
    private static final String KEY_CAM_CLS = "pref_camera_cls";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent == null || intent.getAction() == null) return;
        String action = intent.getAction();
        Log.i(TAG, "Hardware / System Broadcast recibido: " + action);

        // 1. Boton HOME del timon, consola central o gesto swipe Changan
        if ("com.chinatsp.launcher_KEYHOME_SWIPE".equals(action)
                || "com.chinatsp.action.ACTION_KEYHOME_SWIPE".equals(action)
                || "com.chinatsp.action.HOME".equals(action)
                || "com.chinatsp.launcher.home".equals(action)
                || "com.chinatsp.systemui.ACTION_HOME".equals(action)
                || "android.intent.action.CLOSE_SYSTEM_DIALOGS".equals(action)) {
            bringLauncherToFront(context);
            return;
        }

        // 2. Eventos de teclas fisicas CoAgent (timon y consola central F202)
        if ("com.coagent.intent.action.KEY_CHANGED".equals(action)) {
            int keyCode = intent.getIntExtra("Key_code", intent.getIntExtra("keyCode", intent.getIntExtra("key_code", -1)));
            String keyStr = intent.getStringExtra("Key_code");
            if (keyStr == null) keyStr = intent.getStringExtra("key");
            if (keyStr == null) keyStr = intent.getStringExtra("key_code");
            String keyState = intent.getStringExtra("Key_state");

            Log.i(TAG, "CoAgent Key_code: " + keyCode + " | keyStr: " + keyStr + " | keyState: " + keyState);

            // Tecla de camara o AVM del timon (KeyCode 27, 212, 213, 220, 221 o texto avm/cam/camera/view)
            boolean isCamKey = (keyCode == 27 || keyCode == 212 || keyCode == 213 || keyCode == 220 || keyCode == 221);
            if (!isCamKey && keyStr != null) {
                String kLower = keyStr.toLowerCase();
                isCamKey = kLower.contains("cam") || kLower.contains("avm") || kLower.contains("360") || kLower.contains("view");
            }

            if (isCamKey) {
                triggerAvm360(context);
                return;
            }

            // Tecla HOME / SRC del timon o consola (KeyCode 3 o texto home/src/menu)
            boolean isHomeKey = (keyCode == 3);
            if (!isHomeKey && keyStr != null) {
                String kLower = keyStr.toLowerCase();
                isHomeKey = kLower.contains("home") || "src".equalsIgnoreCase(kLower) || "menu".equalsIgnoreCase(kLower);
            }

            if (isHomeKey) {
                bringLauncherToFront(context);
                return;
            }
        }

        // 3. Conexion Bluetooth / Wi-Fi
        if (BluetoothDevice.ACTION_ACL_CONNECTED.equals(action)
                || "android.net.wifi.STATE_CHANGE".equals(action)
                || "android.net.conn.CONNECTIVITY_CHANGE".equals(action)) {
            Log.i(TAG, "Conexion de dispositivo detectada (" + action + ").");
        }
    }

    public static void bringLauncherToFront(Context context) {
        // Cerrar dialogos del sistema y ajustes de configuracion
        try {
            context.sendBroadcast(new Intent(Intent.ACTION_CLOSE_SYSTEM_DIALOGS));
            context.sendBroadcast(new Intent("com.chinatsp.action.HOME"));
            context.sendBroadcast(new Intent("com.chinatsp.systemui.ACTION_HOME"));
        } catch (Exception ignored) {}

        // Invocacion a traves del servicio flotante si esta vivo
        try {
            FloatingOverlayService fos = FloatingOverlayService.getInstance();
            if (fos != null) {
                fos.triggerHome();
                return;
            }
        } catch (Exception ignored) {}

        // Intent explicito con maxima prioridad al frente
        try {
            Intent homeIntent = new Intent(context, MainActivity.class);
            homeIntent.setAction(Intent.ACTION_MAIN);
            homeIntent.addCategory(Intent.CATEGORY_HOME);
            homeIntent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK
                    | Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED
                    | Intent.FLAG_ACTIVITY_CLEAR_TOP
                    | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT
                    | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            context.startActivity(homeIntent);
        } catch (Exception e) {
            try {
                Intent fallback = new Intent(Intent.ACTION_MAIN);
                fallback.addCategory(Intent.CATEGORY_HOME);
                fallback.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(fallback);
            } catch (Exception ignored) {}
            Log.w(TAG, "Error elevando Launcher al frente: " + e.getMessage());
        }
    }

    public static void triggerAvm360(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        String savedPkg = prefs.getString(KEY_CAM_PKG, "com.chinatsp.avmlive");
        String savedCls = prefs.getString(KEY_CAM_CLS, "com.chinatsp.avmlive.MainActivity");

        PackageManager pm = context.getPackageManager();

        // 1. Intentar lanzar la app configurada (Por defecto com.chinatsp.avmlive - Camara 360 Real de Fabrica)
        try {
            Intent camIntent = new Intent();
            camIntent.setComponent(new ComponentName(savedPkg, savedCls));
            camIntent.setAction(Intent.ACTION_MAIN);
            camIntent.addCategory(Intent.CATEGORY_LAUNCHER);
            camIntent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED);
            context.startActivity(camIntent);
            Log.i(TAG, "Camara 360 lanzada con exito: " + savedPkg + "/" + savedCls);
            return;
        } catch (Exception e) {
            Log.w(TAG, "No se pudo abrir componente configurado " + savedPkg + ": " + e.getMessage());
        }

        // 2. Si no abre el componente exacto, intentar LaunchIntent del paquete
        try {
            Intent launch = pm.getLaunchIntentForPackage(savedPkg);
            if (launch != null) {
                launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(launch);
                return;
            }
        } catch (Exception ignored) {}

        // 3. Fallback: Probar BuiltinHDCameraActivity de Changan
        try {
            Intent camHd = new Intent();
            camHd.setComponent(new ComponentName("com.chinatsp.dvrcamera", "com.chinatsp.dvrcamera.builtin.hdcamera.BuiltinHDCameraActivity"));
            camHd.setAction("android.chinatsp.intent.action.customize_camera");
            camHd.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED);
            context.startActivity(camHd);
            return;
        } catch (Exception ignored) {}

        // 4. Fallback por Broadcasts oficiales OEM de Hardware AVM Changan
        try {
            context.sendBroadcast(new Intent("com.chinatsp.action.AVM_ON"));
            context.sendBroadcast(new Intent("com.chinatsp.action.AVM_DISPLAY_SWITCH"));
            context.sendBroadcast(new Intent("com.chinatsp.action.ENTER_AVM"));
            context.sendBroadcast(new Intent("com.chinatsp.systemui.ACTION_ENTER_AVM"));
            context.sendBroadcast(new Intent("changan.os.action.to.user.center.view.fullsrceen"));
            Intent evsService = new Intent("video.evs.camera.HDCameraService");
            evsService.setPackage("video.evs.camera");
            context.startService(evsService);
        } catch (Exception ignored) {}
    }
}
