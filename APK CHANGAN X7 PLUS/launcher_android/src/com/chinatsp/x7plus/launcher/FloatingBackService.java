package com.chinatsp.x7plus.launcher;

import android.accessibilityservice.AccessibilityService;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.util.Log;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.view.accessibility.AccessibilityEvent;
import android.widget.ImageView;

/**
 * Servicio Automotriz Flotante de Retroceso y Home (Floating Back & Home Bubble)
 * Funciona de forma dual: como AccessibilityService para inyección global inmediata de BACK y HOME,
 * y como Overlay Window visible sobre cualquier aplicación (Waze, YouTube, Brave, etc.).
 */
public class FloatingBackService extends AccessibilityService {

    private static final String TAG = "FloatingBackService";
    private WindowManager windowManager;
    private View bubbleView;
    private WindowManager.LayoutParams params;
    private static FloatingBackService sInstance;

    public static FloatingBackService getInstance() {
        return sInstance;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        sInstance = this;
        windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);
        createFloatingBubble();
    }

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        sInstance = this;
        Log.i(TAG, "AccessibilityService conectado con exito.");
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        // Eventos pasivos para no consumir CPU
    }

    @Override
    public void onInterrupt() {
        Log.w(TAG, "AccessibilityService interrumpido.");
    }

    private void createFloatingBubble() {
        // Desactivado: Solo FloatingOverlayService crea la unica burbuja visual sutil (38dp, 0.35 alpha)
    }

    public void doBack() {
        boolean ok = false;
        try {
            ok = performGlobalAction(GLOBAL_ACTION_BACK);
        } catch (Exception ignored) {}

        if (!ok) {
            new Thread(new Runnable() {
                @Override
                public void run() {
                    try {
                        Runtime.getRuntime().exec("input keyevent 4");
                    } catch (Exception ignored) {}
                }
            }).start();
        }
    }

    public void doHome() {
        boolean ok = false;
        try {
            ok = performGlobalAction(GLOBAL_ACTION_HOME);
        } catch (Exception ignored) {}

        if (!ok) {
            try {
                Intent home = new Intent(this, MainActivity.class);
                home.setAction(Intent.ACTION_MAIN);
                home.addCategory(Intent.CATEGORY_HOME);
                home.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
                startActivity(home);
            } catch (Exception ignored) {}
        }
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
