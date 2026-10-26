package com.chinatsp.x7plus.launcher;

import android.app.Instrumentation;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.IBinder;
import android.provider.Settings;
import android.util.Log;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.ImageView;

/**
 * Servicio Automotriz Independiente para la Burbuja Flotante de Retroceso y Home.
 * Diseno: Casi imperceptible (translucido sutil, cristal oscuro, estilo minimalista OEM).
 * Solo 1 burbuja en todo el sistema.
 */
public class FloatingOverlayService extends Service {

    private static final String TAG = "FloatingOverlayService";
    private WindowManager windowManager;
    private View bubbleView;
    private WindowManager.LayoutParams params;
    private static FloatingOverlayService sInstance;

    public static FloatingOverlayService getInstance() {
        return sInstance;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        sInstance = this;
        windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);
        showFloatingBubble();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        showFloatingBubble();
        return START_STICKY;
    }

    public void showFloatingBubble() {
        if (bubbleView != null) {
            try {
                bubbleView.setVisibility(View.VISIBLE);
            } catch (Exception ignored) {}
            return;
        }

        // Verificar permiso de overlay
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (!Settings.canDrawOverlays(this)) {
                Log.w(TAG, "Permiso de overlay no concedido aun.");
                return;
            }
        }

        int layoutType;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            layoutType = WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY;
        } else {
            layoutType = WindowManager.LayoutParams.TYPE_SYSTEM_ALERT;
        }

        // Medidas sutiles: 38dp x 38dp (discreto, casi imperceptible)
        params = new WindowManager.LayoutParams(
            dpToPx(38),
            dpToPx(38),
            layoutType,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            PixelFormat.TRANSLUCENT
        );

        // Opacidad muy baja por defecto (casi invisible para no molestar la vista)
        params.alpha = 0.35f;
        params.gravity = Gravity.TOP | Gravity.START;
        params.x = 12;
        params.y = dpToPx(180);

        // Vista de la burbuja (Diseno Glassmorphism ultra-discreto)
        ImageView button = new ImageView(this);
        GradientDrawable bg = new GradientDrawable();
        bg.setShape(GradientDrawable.OVAL);
        bg.setColor(Color.parseColor("#33000000")); // Cristal negro traslucido 20%
        bg.setStroke(dpToPx(1), Color.parseColor("#44FFFFFF")); // Borde sutil blanco traslucido
        button.setBackground(bg);
        button.setImageResource(R.drawable.ic_skip_prev); // Flecha chevron de retroceso
        button.setPadding(dpToPx(9), dpToPx(9), dpToPx(9), dpToPx(9));
        button.setColorFilter(Color.parseColor("#99FFFFFF")); // Icono blanco traslucido
        button.setContentDescription("Boton Flotante Retroceso");

        bubbleView = button;

        bubbleView.setOnTouchListener(new View.OnTouchListener() {
            private int initialX;
            private int initialY;
            private float initialTouchX;
            private float initialTouchY;
            private long touchStartTime;

            @Override
            public boolean onTouch(View v, MotionEvent event) {
                switch (event.getAction()) {
                    case MotionEvent.ACTION_DOWN:
                        initialX = params.x;
                        initialY = params.y;
                        initialTouchX = event.getRawX();
                        initialTouchY = event.getRawY();
                        touchStartTime = System.currentTimeMillis();
                        // Al tocar, aumentar ligeramente la visibilidad
                        params.alpha = 0.75f;
                        try {
                            windowManager.updateViewLayout(bubbleView, params);
                        } catch (Exception ignored) {}
                        return true;

                    case MotionEvent.ACTION_MOVE:
                        params.x = initialX + (int) (event.getRawX() - initialTouchX);
                        params.y = initialY + (int) (event.getRawY() - initialTouchY);
                        try {
                            windowManager.updateViewLayout(bubbleView, params);
                        } catch (Exception ignored) {}
                        return true;

                    case MotionEvent.ACTION_UP:
                        // Restaurar opacidad casi imperceptible
                        params.alpha = 0.35f;
                        try {
                            windowManager.updateViewLayout(bubbleView, params);
                        } catch (Exception ignored) {}

                        float diffX = Math.abs(event.getRawX() - initialTouchX);
                        float diffY = Math.abs(event.getRawY() - initialTouchY);
                        long duration = System.currentTimeMillis() - touchStartTime;

                        if (diffX < 20 && diffY < 20) {
                            if (duration > 500) {
                                // Pulsacion larga sostenida -> Volver al HOME Launcher
                                triggerHome();
                            } else {
                                // Toque corto -> Ejecutar accion de retroceso BACK 100% funcional
                                triggerBack();
                            }
                        }
                        return true;
                }
                return false;
            }
        });

        try {
            windowManager.addView(bubbleView, params);
            Log.i(TAG, "Burbuja flotante de retroceso sutil superpuesta con exito.");
        } catch (Exception e) {
            Log.e(TAG, "Error al mostrar burbuja flotante", e);
        }
    }

    public void triggerBack() {
        // 1. AccessibilityService si esta activo
        FloatingBackService abs = FloatingBackService.getInstance();
        if (abs != null) {
            try {
                abs.doBack();
                return;
            } catch (Exception ignored) {}
        }

        // 2. Inyeccion limpia via Instrumentation y consola
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    Instrumentation inst = new Instrumentation();
                    inst.sendKeyDownUpSync(KeyEvent.KEYCODE_BACK);
                } catch (Throwable t) {
                    try {
                        Runtime.getRuntime().exec("input keyevent 4");
                    } catch (Exception ignored) {}
                }
            }
        }).start();

        // 3. Broadcasts OEM Changan
        try {
            sendBroadcast(new Intent("com.chinatsp.action.BACK"));
            Intent coagent = new Intent("com.coagent.intent.action.KEY_CHANGED");
            coagent.putExtra("key_code", 4);
            sendBroadcast(coagent);
        } catch (Exception ignored) {}
    }

    public void triggerHome() {
        FloatingBackService abs = FloatingBackService.getInstance();
        if (abs != null) {
            try {
                abs.doHome();
                return;
            } catch (Exception ignored) {}
        }

        try {
            Intent home = new Intent(Intent.ACTION_MAIN);
            home.addCategory(Intent.CATEGORY_HOME);
            home.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
            startActivity(home);
        } catch (Exception ignored) {}
    }

    private int dpToPx(int dp) {
        float density = getResources().getDisplayMetrics().density;
        return Math.round((float) dp * density);
    }

    @Override
    public void onDestroy() {
        sInstance = null;
        if (bubbleView != null && windowManager != null) {
            try {
                windowManager.removeView(bubbleView);
            } catch (Exception ignored) {}
            bubbleView = null;
        }
        super.onDestroy();
    }
}
