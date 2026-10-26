package com.chinatsp.x7plus.launcher;

import android.app.Activity;
import android.app.Dialog;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothProfile;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.graphics.Bitmap;

import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.Typeface;
import android.graphics.BitmapFactory;
import android.graphics.drawable.ColorDrawable;
import android.os.Environment;
import java.io.File;
import java.io.InputStream;
import java.io.FileOutputStream;
import java.io.FileFilter;
import java.util.Random;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.drawable.Drawable;
import android.view.GestureDetector;
import android.view.MotionEvent;
import android.widget.ViewFlipper;

import android.graphics.PixelFormat;
import android.media.AudioManager;
import android.media.MediaPlayer;
import android.net.Uri;
import android.os.Bundle;
import android.os.SystemClock;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowManager;
import android.widget.AdapterView;
import android.widget.BaseAdapter;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.GridView;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.VideoView;

import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import android.content.BroadcastReceiver;
import android.content.IntentFilter;
import android.net.wifi.WifiManager;
import android.text.format.Formatter;

public class MainActivity extends Activity implements MediaNotificationListener.MediaListener {

    private static final String PREFS_NAME = "CockpitX7Prefs";
    private static final String KEY_DEFAULT_MUSIC = "default_music_package";
    private static final String KEY_DRIVE_MODE = "saved_drive_mode";
    private static final String KEY_LAST_INTRO_TIME = "last_intro_played_timestamp";
    private static final long INTRO_COOLDOWN_MS = 5 * 60 * 60 * 1000L; // 5 Horas de enfriamiento

    // UI Elements
    private ImageButton btnMediaPlay;
    private TextView tvTrackStatus;
    private TextView tvTrackTitle;
    private TextView tvTrackArtist;
    private ImageView ivAlbumArt;
    private boolean isPlaying = true;

    // GPS Status UI Elements
    private View pillGpsStatus;
    private View dotGpsStatus;
    private TextView tvGpsStatus;

    // Bluetooth Status Elements
    private TextView tvPhoneBadge;

    // Intro Video Elements
    private View videoOverlayContainer;
    private FullScreenVideoView videoIntroView;
    private MediaPlayer introMediaPlayer;
    private boolean isVideoMuted = false;

    // Night Mode Overlay
    private View nightModeOverlay;

    // Wallpaper & Personalization Elements
    private static final String KEY_WALLPAPER_RES = "custom_wallpaper_res";
    private static final String KEY_WALLPAPER_PATH = "custom_wallpaper_path";
    private static final String KEY_VIDEO_MODE = "video_startup_mode"; // 0=Siempre, 1=Enfriamiento 30m, 2=Desactivado
    private static final String KEY_VIDEO_RANDOM = "video_random_enabled";
    private static final int REQ_PICK_WALLPAPER = 1001;

    private ImageView ivBg;
    private static boolean sHasPlayedIntroThisBoot = false;
    private ImageButton btnClearCache;

    private SharedPreferences prefs;

    // ViewFlipper & Second Home Elements
    private ViewFlipper viewFlipper;
    private View dotPage1;
    private View dotPage2;
    private GestureDetector gestureDetector;
    private GridView gvSecondHome;

    private BroadcastReceiver dynamicHardwareKeyReceiver;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);

        // 1. Hardware accelerated fullscreen window
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        Window window = getWindow();
        window.clearFlags(WindowManager.LayoutParams.FLAG_TRANSLUCENT_STATUS
                        | WindowManager.LayoutParams.FLAG_TRANSLUCENT_NAVIGATION);
        window.addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN
                      | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN
                      | WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS
                      | WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.P) {
            WindowManager.LayoutParams lp = window.getAttributes();
            lp.layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
            window.setAttributes(lp);
        }

        setImmersiveMode();
        enforceFullScreenBounds();
        unlockChanganF202Fullscreen();

        window.getDecorView().setOnSystemUiVisibilityChangeListener(new View.OnSystemUiVisibilityChangeListener() {
            @Override
            public void onSystemUiVisibilityChange(int visibility) {
                if ((visibility & View.SYSTEM_UI_FLAG_FULLSCREEN) == 0) {
                    setImmersiveMode();
                }
            }
        });

        setContentView(R.layout.activity_main);

        // Diagnóstico de dimensiones reales en pantalla
        logScreenDiagnostics();

        // 2. Initialize Views
        initViews();

        // 3. Setup Components
        setupSidebarButtons();
        setupTopTabs();
        setupMediaControls();
        setupSixMainCards();
        setupBottomFavoritesDock();
        setupTopBarButtons();
        setupGpsStatus();
        setupNightMode();

        // 4. Setup Dynamic Media Listener
        MediaNotificationListener.setMediaListener(this);

        // 5. Setup ViewFlipper Gestures & Second Home
        setupPageGestures();

        // 6. Start Native Floating Back & Home Services
        try {
            startService(new Intent(this, FloatingOverlayService.class));
        } catch (Exception ignored) {}
        // FloatingBackService eliminado para mantener exactamente 1 sola burbuja discreta

        // 7. Start GPS Real-Time Hardware Telemetry Service
        try {
            startService(new Intent(this, MockLocationService.class));
        } catch (Exception ignored) {}

        // 8. Handle Intro Video on Cold Start with 5-Hour Smart Cooldown
        setupStartupVideo();
    }

    
    @Override
    public boolean dispatchTouchEvent(MotionEvent ev) {
        if (gestureDetector != null) {
            gestureDetector.onTouchEvent(ev);
        }
        return super.dispatchTouchEvent(ev);
    }

    private void initViews() {
        ivBg = findViewById(R.id.iv_bg);
        applySavedWallpaper();

        if (ivBg != null) {
            ivBg.setOnLongClickListener(new View.OnLongClickListener() {
                @Override
                public boolean onLongClick(View v) {
                    showPersonalizationDialog();
                    return true;
                }
            });
        }

        View rootLayout = findViewById(R.id.root_layout);
        if (rootLayout != null) {
            rootLayout.setOnLongClickListener(new View.OnLongClickListener() {
                @Override
                public boolean onLongClick(View v) {
                    showPersonalizationDialog();
                    return true;
                }
            });
        }

        btnMediaPlay = findViewById(R.id.btn_media_play);
        tvTrackStatus = findViewById(R.id.tv_track_status);
        tvTrackTitle = findViewById(R.id.tv_track_title);
        tvTrackArtist = findViewById(R.id.tv_track_artist);
        ivAlbumArt = findViewById(R.id.iv_album_art);

        pillGpsStatus = findViewById(R.id.pill_gps_status);
        dotGpsStatus = findViewById(R.id.dot_gps_status);
        tvGpsStatus = findViewById(R.id.tv_gps_status);

        videoOverlayContainer = findViewById(R.id.video_overlay_container);
        videoIntroView = findViewById(R.id.video_intro_view);
        nightModeOverlay = findViewById(R.id.night_mode_overlay);

        btnClearCache = findViewById(R.id.btn_clear_cache);
        if (btnClearCache != null) {
            btnClearCache.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    clearLauncherCacheAndRefresh();
                }
            });
        }
    }

    private void setImmersiveMode() {
        View decorView = getWindow().getDecorView();
        decorView.setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_FULLSCREEN
            | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
        );
    }

    /**
     * Asegura que la ventana ocupe la pantalla completa sin límites de decoración.
     */
    private void enforceFullScreenBounds() {
        try {
            Window window = getWindow();
            if (window == null) return;
            WindowManager.LayoutParams attrs = window.getAttributes();
            attrs.width = WindowManager.LayoutParams.MATCH_PARENT;
            attrs.height = WindowManager.LayoutParams.MATCH_PARENT;
            attrs.gravity = Gravity.FILL;

            // Eliminamos FLAG_LAYOUT_INSET_DECOR para evitar que WindowManager aplique márgenes
            attrs.flags &= ~WindowManager.LayoutParams.FLAG_LAYOUT_INSET_DECOR;
            attrs.flags &= ~WindowManager.LayoutParams.FLAG_TRANSLUCENT_STATUS;
            attrs.flags &= ~WindowManager.LayoutParams.FLAG_TRANSLUCENT_NAVIGATION;

            attrs.flags |= WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN
                         | WindowManager.LayoutParams.FLAG_FULLSCREEN
                         | WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS;

            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.P) {
                attrs.layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
            }
            window.setAttributes(attrs);

            // Consumir WindowInsets para evitar paddings automáticos de barras laterales
            window.getDecorView().setOnApplyWindowInsetsListener(new View.OnApplyWindowInsetsListener() {
                @Override
                public android.view.WindowInsets onApplyWindowInsets(View v, android.view.WindowInsets insets) {
                    return insets.consumeSystemWindowInsets();
                }
            });
        } catch (Exception ignored) {
        }
    }

    private void logScreenDiagnostics() {
        try {
            android.util.DisplayMetrics dm = getResources().getDisplayMetrics();
            android.view.Display display = getWindowManager().getDefaultDisplay();
            android.graphics.Point realSize = new android.graphics.Point();
            display.getRealSize(realSize);
            android.util.Log.i("CockpitX7_Fullscreen", "=== DIAGNOSTICO DE PANTALLA COCKPIT X7 ===");
            android.util.Log.i("CockpitX7_Fullscreen", "DisplayMetrics: " + dm.widthPixels + "x" + dm.heightPixels + " (" + dm.densityDpi + " dpi)");
            android.util.Log.i("CockpitX7_Fullscreen", "Display.getRealSize: " + realSize.x + "x" + realSize.y);
            android.util.Log.i("CockpitX7_Fullscreen", "Relacion de Aspecto: " + ((float) realSize.x / Math.max(1, realSize.y)));
        } catch (Exception ignored) {}
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            setImmersiveMode();
        }
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        setImmersiveMode();
        dismissIntroVideo(); // Garantizar que no suene ni se muestre al regresar al HOME
    }

    @Override
    protected void onResume() {
        super.onResume();
        dismissIntroVideo();
        try {
            startService(new Intent(this, FloatingOverlayService.class));
        } catch (Exception ignored) {}
        setImmersiveMode();
        unlockChanganF202Fullscreen();
        registerHardwareKeyReceiver();
        updateGpsStatusUI();
        updateBluetoothStatusUI();
    }

    @Override
    protected void onPause() {
        super.onPause();
        unregisterHardwareKeyReceiver();
    }

    @Override
    protected void onDestroy() {
        MediaNotificationListener.setMediaListener(null);
        unregisterHardwareKeyReceiver();
        super.onDestroy();
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        // 1. Tecla HOME del timón o consola
        if (keyCode == KeyEvent.KEYCODE_HOME) {
            if (videoOverlayContainer != null && videoOverlayContainer.getVisibility() == View.VISIBLE) {
                dismissIntroVideo();
                return true;
            }
            if (nightModeOverlay != null && nightModeOverlay.getVisibility() == View.VISIBLE) {
                nightModeOverlay.setVisibility(View.GONE);
                setImmersiveMode();
                return true;
            }
            setImmersiveMode();
            return true;
        }

        // 2. Tecla Cámara 360° del timón / consola (KeyCode 27 o KEYCODE_CAMERA)
        // Permitir que el sistema nativo del Changan X7 Plus abra las cámaras de guía 360° (2D/3D/estacionamiento) sin secuestrar la tecla para el DVR
        if (keyCode == KeyEvent.KEYCODE_CAMERA || keyCode == 27) {
            triggerAvm360Broadcasts();
            return false;
        }

        return super.onKeyDown(keyCode, event);
    }

    @Override
    public void onBackPressed() {
        // Dismiss video or night mode if active, else stay in launcher
        if (videoOverlayContainer != null && videoOverlayContainer.getVisibility() == View.VISIBLE) {
            dismissIntroVideo();
            return;
        }
        if (nightModeOverlay != null && nightModeOverlay.getVisibility() == View.VISIBLE) {
            nightModeOverlay.setVisibility(View.GONE);
            return;
        }
        setImmersiveMode();
    }

    // ========================================================================
    // 1. STARTUP INTRO VIDEO & RANDOM WELCOME VIDEO SYSTEM
    // ========================================================================
    private Uri getWelcomeVideoUri() {
        try {
            File dir = new File(Environment.getExternalStorageDirectory(), "Changan/Videos");
            if (!dir.exists()) {
                dir.mkdirs();
            }
            File[] files = dir.listFiles(new FileFilter() {
                @Override
                public boolean accept(File file) {
                    if (file.isFile()) {
                        String name = file.getName().toLowerCase();
                        return name.endsWith(".mp4") || name.endsWith(".mkv") || name.endsWith(".webm");
                    }
                    return false;
                }
            });
            if (files != null && files.length > 0) {
                boolean isRandom = prefs.getBoolean(KEY_VIDEO_RANDOM, true);
                if (isRandom) {
                    int index = new Random().nextInt(files.length);
                    return Uri.fromFile(files[index]);
                } else {
                    return Uri.fromFile(files[0]);
                }
            }
        } catch (Exception ignored) {}
        // Fallback al video de bienvenida integrado en el APK
        return Uri.parse("android.resource://" + getPackageName() + "/" + R.raw.intro_video);
    }

    private void setupStartupVideo() {
        if (sHasPlayedIntroThisBoot) {
            dismissIntroVideo();
            return;
        }

        long currentUptime = android.os.SystemClock.elapsedRealtime();
        // ESTRICTO: Solo reproducir si el vehículo arrancó en frío hace menos de 120 segundos (2 minutos)
        // Evita al 100% que al volver al Home se active el video o sonido
        if (currentUptime > 120_000L) {
            sHasPlayedIntroThisBoot = true;
            dismissIntroVideo();
            return;
        }

        int mode = prefs.getInt(KEY_VIDEO_MODE, 1);
        if (mode == 2) { // 2 = Desactivado permanentemente
            dismissIntroVideo();
            return;
        }

        long lastPlayed = prefs.getLong(KEY_LAST_INTRO_TIME, 0);
        long now = System.currentTimeMillis();
        long diff = now - lastPlayed;
        long COOLDOWN_12_HOURS = 12 * 60 * 60 * 1000L;
        if (lastPlayed > 0 && diff > 0 && diff < COOLDOWN_12_HOURS) {
            sHasPlayedIntroThisBoot = true;
            dismissIntroVideo();
            return;
        }

        // Registrar timestamp permanente
        prefs.edit()
            .putLong(KEY_LAST_INTRO_TIME, now)
            .apply();

        playIntroVideo(false);
    }

    private void playIntroVideo(boolean isTest) {
        if (!isTest) sHasPlayedIntroThisBoot = true;
        if (videoOverlayContainer == null || videoIntroView == null) return;

        videoOverlayContainer.setVisibility(View.VISIBLE);
        videoOverlayContainer.bringToFront();
        setImmersiveMode();

        final Button btnSkip = findViewById(R.id.btn_skip_video);
        final Button btnMute = findViewById(R.id.btn_mute_video);

        // Tap en cualquier parte de la pantalla omite el video instantáneamente
        videoOverlayContainer.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dismissIntroVideo();
            }
        });

        if (btnSkip != null) {
            btnSkip.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    dismissIntroVideo();
                }
            });
        }

        if (btnMute != null) {
            btnMute.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    isVideoMuted = !isVideoMuted;
                    if (introMediaPlayer != null) {
                        float vol = isVideoMuted ? 0.0f : 0.25f;
                        introMediaPlayer.setVolume(vol, vol);
                    }
                    btnMute.setText(isVideoMuted ? "🔊 Sonido" : "🔇 Silenciar");
                }
            });
        }

        try {
            Uri videoUri = getWelcomeVideoUri();
            videoIntroView.setVideoURI(videoUri);
            videoIntroView.setOnPreparedListener(new MediaPlayer.OnPreparedListener() {
                @Override
                public void onPrepared(MediaPlayer mp) {
                    if (videoOverlayContainer == null || videoOverlayContainer.getVisibility() != View.VISIBLE) {
                        try {
                            mp.stop();
                            mp.reset();
                            mp.release();
                        } catch (Exception ignored) {}
                        return;
                    }
                    introMediaPlayer = mp;
                    float vol = isVideoMuted ? 0.0f : 0.25f;
                    mp.setVolume(vol, vol);
                    mp.start();
                }
            });
            videoIntroView.setOnCompletionListener(new MediaPlayer.OnCompletionListener() {
                @Override
                public void onCompletion(MediaPlayer mp) {
                    dismissIntroVideo();
                }
            });
            videoIntroView.setOnErrorListener(new MediaPlayer.OnErrorListener() {
                @Override
                public boolean onError(MediaPlayer mp, int what, int extra) {
                    dismissIntroVideo();
                    return true;
                }
            });
        } catch (Exception e) {
            dismissIntroVideo();
        }
    }

    private void dismissIntroVideo() {
        sHasPlayedIntroThisBoot = true;
        if (introMediaPlayer != null) {
            try {
                introMediaPlayer.stop();
                introMediaPlayer.reset();
                introMediaPlayer.release();
            } catch (Exception ignored) {}
            introMediaPlayer = null;
        }
        if (videoIntroView != null) {
            try {
                videoIntroView.stopPlayback();
            } catch (Exception ignored) {}
        }
        if (videoOverlayContainer != null) {
            videoOverlayContainer.setVisibility(View.GONE);
        }
        setImmersiveMode();
    }

    // ========================================================================
    // 2. NIGHT MODE (TOTAL BLACK SCREEN OVERLAY - TAP TO WAKE)
    // ========================================================================
    private void setupNightMode() {
        if (nightModeOverlay != null) {
            nightModeOverlay.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    nightModeOverlay.setVisibility(View.GONE);
                    setImmersiveMode();
                }
            });
        }
    }

    private void activateNightMode() {
        if (nightModeOverlay != null) {
            nightModeOverlay.setVisibility(View.VISIBLE);
        }
    }

    // ========================================================================
    // 3. SIDEBAR BUTTONS
    // ========================================================================
    private void setupSidebarButtons() {
        findViewById(R.id.btn_side_home).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showPage(0);
                setImmersiveMode();
            }
        });

        findViewById(R.id.btn_side_nav).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showNavSelectorDialog();
            }
        });

        findViewById(R.id.btn_side_music).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showMusicSelectorDialog();
            }
        });

        findViewById(R.id.btn_side_phone).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchPhone();
            }
        });

        findViewById(R.id.btn_side_apps).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showPage(1);
            }
        });
        findViewById(R.id.btn_side_apps).setOnLongClickListener(new View.OnLongClickListener() {
            @Override
            public boolean onLongClick(View v) {
                showAppDrawer();
                return true;
            }
        });

        findViewById(R.id.btn_side_settings).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showPersonalizationDialog();
            }
        });
        findViewById(R.id.btn_side_settings).setOnLongClickListener(new View.OnLongClickListener() {
            @Override
            public boolean onLongClick(View v) {
                launchSettings();
                return true;
            }
        });
    }

    // ========================================================================
    // 4. DYNAMIC MEDIA CONTROLS & NOTIFICATION LISTENER
    // ========================================================================
    private void setupMediaControls() {
        ImageButton btnMediaPrev = findViewById(R.id.btn_media_prev);
        ImageButton btnMediaNext = findViewById(R.id.btn_media_next);

        if (btnMediaPrev != null) {
            btnMediaPrev.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    dispatchMediaKey(KeyEvent.KEYCODE_MEDIA_PREVIOUS);
                }
            });
        }

        if (btnMediaPlay != null) {
            btnMediaPlay.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    dispatchMediaKey(KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE);
                }
            });
        }

        if (btnMediaNext != null) {
            btnMediaNext.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    dispatchMediaKey(KeyEvent.KEYCODE_MEDIA_NEXT);
                }
            });
        }

        View musicWidget = findViewById(R.id.music_widget);
        if (musicWidget != null) {
            musicWidget.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    launchMusicPreferredOrSelector();
                }
            });
        }
    }

    private void dispatchMediaKey(int keyCode) {
        AudioManager am = (AudioManager) getSystemService(Context.AUDIO_SERVICE);
        if (am != null) {
            long eventTime = SystemClock.uptimeMillis();
            KeyEvent down = new KeyEvent(eventTime, eventTime, KeyEvent.ACTION_DOWN, keyCode, 0);
            KeyEvent up = new KeyEvent(eventTime, eventTime, KeyEvent.ACTION_UP, keyCode, 0);
            am.dispatchMediaKeyEvent(down);
            am.dispatchMediaKeyEvent(up);
        }

        if (keyCode == KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE) {
            isPlaying = !isPlaying;
            if (btnMediaPlay != null) {
                btnMediaPlay.setImageResource(isPlaying ? R.drawable.ic_pause : R.drawable.ic_play_arrow);
            }
        }
    }

    @Override
    public void onMediaUpdated(final String title, final String artist, final Bitmap albumArt, final boolean playing) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                // Filtrar notificaciones de Maps/Navegación que no son música real
                if (title != null && isNavigationNotification(title, artist)) {
                    return; // Ignorar - no es contenido musical
                }
                if (tvTrackTitle != null && title != null && !title.isEmpty()) {
                    tvTrackTitle.setText(title);
                }
                if (tvTrackArtist != null && artist != null && !artist.isEmpty()) {
                    tvTrackArtist.setText(artist);
                }
                if (tvTrackStatus != null) {
                    tvTrackStatus.setText("Reproduciendo");
                }
                if (ivAlbumArt != null && albumArt != null) {
                    ivAlbumArt.setImageBitmap(albumArt);
                }
                if (btnMediaPlay != null) {
                    isPlaying = playing;
                    btnMediaPlay.setImageResource(isPlaying ? R.drawable.ic_pause : R.drawable.ic_play_arrow);
                }
            }
        });
    }

    /**
     * Filtra notificaciones que NO son de música real (Maps, navegación, etc.)
     * para evitar que el widget de música muestre "maps en segundo plano".
     */
    private boolean isNavigationNotification(String title, String artist) {
        String combined = (title + " " + (artist != null ? artist : "")).toLowerCase();
        String[] navKeywords = {
            "maps", "segundo plano", "en segundo", "navegando", "navigation",
            "gps", "ruta", "dirección", "waze", "magic earth", "background",
            "running in", "map is", "usando tu ubicación", "location"
        };
        for (String keyword : navKeywords) {
            if (combined.contains(keyword)) {
                return true;
            }
        }
        return false;
    }

    // ========================================================================
    // 5. TOP TABS & WORKSPACE NAVIGATION
    // ========================================================================
    private void setupTopTabs() {
        final TextView tabDriving = findViewById(R.id.tab_driving);
        final TextView tabMedia = findViewById(R.id.tab_media);
        final TextView tabSystem = findViewById(R.id.tab_system);

        if (tabDriving != null) {
            tabDriving.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    showPage(0);
                    if (tabDriving != null) {
                        tabDriving.setBackgroundResource(R.drawable.bg_tab_active);
                        tabDriving.setTextColor(Color.WHITE);
                    }
                    if (tabMedia != null) {
                        tabMedia.setBackgroundResource(R.drawable.bg_tab_inactive);
                        tabMedia.setTextColor(Color.parseColor("#C5CED8"));
                    }
                    if (tabSystem != null) {
                        tabSystem.setBackgroundResource(R.drawable.bg_tab_inactive);
                        tabSystem.setTextColor(Color.parseColor("#C5CED8"));
                    }
                }
            });
        }

        if (tabMedia != null) {
            tabMedia.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    showMusicSelectorDialog();
                }
            });
        }

        if (tabSystem != null) {
            tabSystem.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    showQuickControlDialog();
                }
            });
        }
    }

    // ========================================================================
    // 6. THE 6 CENTRAL MAIN CARDS
    // ========================================================================
    private void setupSixMainCards() {
        // Card 1: Navegación GPS (Abre pantalla con cards de apps)
        View cardNav = findViewById(R.id.card_nav);
        if (cardNav != null) {
            cardNav.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    showNavSelectorDialog();
                }
            });
            cardNav.setOnLongClickListener(new View.OnLongClickListener() {
                @Override
                public boolean onLongClick(View v) {
                    showNavSelectorDialog();
                    return true;
                }
            });
        }

        View btnCfgNav = findViewById(R.id.btn_configure_nav);
        if (btnCfgNav != null) {
            btnCfgNav.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    showNavSelectorDialog();
                }
            });
        }

        // Card 2: Música (Abre pantalla con cards de reproductores)
        View cardMusic = findViewById(R.id.card_music);
        if (cardMusic != null) {
            cardMusic.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    showMusicSelectorDialog();
                }
            });
            cardMusic.setOnLongClickListener(new View.OnLongClickListener() {
                @Override
                public boolean onLongClick(View v) {
                    showMusicSelectorDialog();
                    return true;
                }
            });
        }

        // Card 3: Radio (SEPARADO DE MÚSICA - Requerimiento Imagen 3)
        View cardRadio = findViewById(R.id.card_radio);
        if (cardRadio != null) {
            cardRadio.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    launchRadio();
                }
            });
        }

        // Card 4: Teléfono
        View cardPhone = findViewById(R.id.card_phone);
        tvPhoneBadge = findViewById(R.id.tv_phone_badge);
        updateBluetoothStatusUI();
        if (cardPhone != null) {
            cardPhone.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    launchPhone();
                }
            });
        }

        // Card 5: Cámara 360° AVM (Abre pantalla con selector AVM/DVR/HD/CAN)
        View cardCam = findViewById(R.id.card_camera);
        if (cardCam != null) {
            cardCam.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    showCameraSelectorDialog();
                }
            });
            cardCam.setOnLongClickListener(new View.OnLongClickListener() {
                @Override
                public boolean onLongClick(View v) {
                    showCameraSelectorDialog();
                    return true;
                }
            });
        }

        // Card 6: Vehículo
        View cardCar = findViewById(R.id.card_car);
        if (cardCar != null) {
            cardCar.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    launchVehicle();
                }
            });
            cardCar.setOnLongClickListener(new View.OnLongClickListener() {
                @Override
                public boolean onLongClick(View v) {
                    showQuickControlDialog();
                    return true;
                }
            });
        }

        // Clima en Widget Superior Compacto (Reubica la caja grande A/C a la cabecera)
        View widgetClimate = findViewById(R.id.widget_climate_top);
        if (widgetClimate != null) {
            widgetClimate.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    launchClimate();
                }
            });
            widgetClimate.setOnLongClickListener(new View.OnLongClickListener() {
                @Override
                public boolean onLongClick(View v) {
                    showQuickControlDialog();
                    return true;
                }
            });
        }
    }

    // ========================================================================
    // 7. BOTTOM FAVORITES DOCK
    // ========================================================================
    private void setupBottomFavoritesDock() {
        // Pill 0: Android Auto / Headunit Reloaded
        View btnFavHu = findViewById(R.id.btn_fav_headunit);
        if (btnFavHu != null) {
            btnFavHu.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    launchHeadunit();
                }
            });
            btnFavHu.setOnLongClickListener(new View.OnLongClickListener() {
                @Override
                public boolean onLongClick(View v) {
                    showHeadunitConnectDialog();
                    return true;
                }
            });
        }

        // Pills personalizables
        loadFavoritePill(1, R.id.btn_fav_radio, R.id.iv_fav_radio, R.id.tv_fav_radio, "com.chinatsp.radio", "Radio", R.drawable.ic_fav_radio);
        loadFavoritePill(2, R.id.btn_fav_music, R.id.iv_fav_music, R.id.tv_fav_music, "com.chinatsp.music", "Reproductor de música", R.drawable.ic_fav_music);
        loadFavoritePill(3, R.id.btn_fav_phone, R.id.iv_fav_phone, R.id.tv_fav_phone, "com.chinatsp.phone", "Teléfono Bluetooth", R.drawable.ic_fav_phone);
        loadFavoritePill(4, R.id.btn_fav_brave, R.id.iv_fav_brave, R.id.tv_fav_brave, "com.brave.browser", "Brave", R.drawable.icon_brave);
    }

    private void loadFavoritePill(final int index, int pillId, int ivId, int tvId, final String defaultPkg, final String defaultLabel, final int defaultIconRes) {
        View pill = findViewById(pillId);
        final ImageView iv = findViewById(ivId);
        final TextView tv = findViewById(tvId);
        if (pill == null) return;

        final String prefPkgKey = "fav_pill_" + index + "_pkg";
        final String prefLabelKey = "fav_pill_" + index + "_label";

        String pkg = prefs.getString(prefPkgKey, defaultPkg);
        String label = prefs.getString(prefLabelKey, defaultLabel);

        if (tv != null) {
            tv.setText(label);
        }

        if (iv != null) {
            Drawable icon = null;
            if ("com.brave.browser".equals(pkg)) {
                try { icon = getResources().getDrawable(R.drawable.icon_brave); } catch (Exception ignored) {}
            } else if ("com.waze".equals(pkg)) {
                try { icon = getResources().getDrawable(R.drawable.icon_waze); } catch (Exception ignored) {}
            }
            if (icon == null) {
                try {
                    icon = getPackageManager().getApplicationIcon(pkg);
                } catch (Exception ignored) {}
            }
            if (icon == null && defaultIconRes != 0) {
                try { icon = getResources().getDrawable(defaultIconRes); } catch (Exception ignored) {}
            }
            if (icon != null) {
                iv.setImageDrawable(icon);
            }
        }

        pill.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String curPkg = prefs.getString(prefPkgKey, defaultPkg);
                String curLabel = prefs.getString(prefLabelKey, defaultLabel);

                if (index == 0 || (curPkg != null && curPkg.toLowerCase().contains("radio"))) {
                    launchRadio();
                    return;
                }
                if (index == 1 && (curPkg != null && curPkg.toLowerCase().contains("music"))) {
                    launchMusicPreferredOrSelector();
                    return;
                }
                if (index == 2 && (curPkg != null && curPkg.toLowerCase().contains("phone"))) {
                    launchPhone();
                    return;
                }
                launchAppOrToast(curPkg, curLabel);
            }
        });

        pill.setOnLongClickListener(new View.OnLongClickListener() {
            @Override
            public boolean onLongClick(View v) {
                showAppPickerForPill(index, prefPkgKey, prefLabelKey, iv, tv);
                return true;
            }
        });
    }

    private void showAppPickerForPill(final int index, final String prefPkgKey, final String prefLabelKey, final ImageView iv, final TextView tv) {
        final Dialog dialog = new Dialog(this, android.R.style.Theme_NoTitleBar_Fullscreen);
        dialog.setContentView(R.layout.dialog_app_drawer);
        setDialogImmersive(dialog);

        TextView title = dialog.findViewById(R.id.drawer_top_bar).findViewById(android.R.id.text1);
        GridView gv = dialog.findViewById(R.id.gv_apps);

        dialog.findViewById(R.id.btn_drawer_close).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dialog.dismiss();
                setImmersiveMode();
            }
        });

        final PackageManager pm = getPackageManager();
        Intent mainIntent = new Intent(Intent.ACTION_MAIN, null);
        mainIntent.addCategory(Intent.CATEGORY_LAUNCHER);
        final List<ResolveInfo> appList = pm.queryIntentActivities(mainIntent, 0);

        Collections.sort(appList, new Comparator<ResolveInfo>() {
            @Override
            public int compare(ResolveInfo a, ResolveInfo b) {
                CharSequence l1 = a.loadLabel(pm);
                CharSequence l2 = b.loadLabel(pm);
                return (l1 != null ? l1.toString() : "").compareToIgnoreCase(l2 != null ? l2.toString() : "");
            }
        });

        if (gv != null) {
            gv.setAdapter(new BaseAdapter() {
                @Override public int getCount() { return appList.size(); }
                @Override public Object getItem(int p) { return appList.get(p); }
                @Override public long getItemId(int p) { return p; }
                @Override
                public View getView(int p, View convertView, ViewGroup parent) {
                    if (convertView == null) {
                        convertView = getLayoutInflater().inflate(R.layout.item_app_drawer, parent, false);
                    }
                    ResolveInfo info = appList.get(p);
                    ImageView itemIv = convertView.findViewById(R.id.iv_app_icon);
                    TextView itemTv = convertView.findViewById(R.id.tv_app_label);
                    if (itemIv != null) {
                        itemIv.setImageDrawable(loadRobustAppIcon(info, pm));
                    }
                    if (itemTv != null) {
                        CharSequence l = info.loadLabel(pm);
                        itemTv.setText(l != null ? l : info.activityInfo.name);
                    }
                    return convertView;
                }
            });

            gv.setOnItemClickListener(new AdapterView.OnItemClickListener() {
                @Override
                public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                    ResolveInfo info = appList.get(position);
                    String selPkg = info.activityInfo.packageName;
                    CharSequence selLabel = info.loadLabel(pm);
                    String labelStr = selLabel != null ? selLabel.toString() : info.activityInfo.name;

                    prefs.edit().putString(prefPkgKey, selPkg).putString(prefLabelKey, labelStr).apply();
                    if (tv != null) tv.setText(labelStr);
                    if (iv != null) iv.setImageDrawable(loadRobustAppIcon(info, pm));

                    Toast.makeText(MainActivity.this, labelStr + " fijado en Favoritos", Toast.LENGTH_SHORT).show();
                    dialog.dismiss();
                    setImmersiveMode();
                }
            });
        }

        dialog.show();
    }

    private void setupTopBarButtons() {
        View btnTopApps = findViewById(R.id.btn_top_apps);
        if (btnTopApps != null) {
            btnTopApps.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    showAppDrawer();
                }
            });
        }

        View btnTopSettings = findViewById(R.id.btn_top_settings);
        if (btnTopSettings != null) {
            btnTopSettings.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    launchSettings();
                }
            });
        }
    }

    // ========================================================================
    // 7. MUSIC SELECTOR DIALOG & PREFERENCES
    // ========================================================================
    private void launchMusicPreferredOrSelector() {
        // Lanzamiento directo a Música OEM Changan sin cuadros de diálogo
        String[] musicPackages = {
            "com.chinatsp.music",
            "com.zionhuang.music",
            "org.schabi.newpipe",
            "org.smarttube.stable",
            "it.fast4x.rimusic"
        };
        for (String pkg : musicPackages) {
            Intent intent = getPackageManager().getLaunchIntentForPackage(pkg);
            if (intent != null) {
                applyFullscreenBypass(pkg);
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(intent);
                return;
            }
        }
        launchExplicit("com.chinatsp.music", "com.chinatsp.music.MainActivity", "Música Changan");
    }

    private void showMusicSelectorDialog() {
        final Dialog dialog = new Dialog(this, android.R.style.Theme_NoTitleBar_Fullscreen);
        dialog.setContentView(R.layout.dialog_music_selector);
        setDialogImmersive(dialog);

        final CheckBox cbRemember = dialog.findViewById(R.id.cb_remember_music);

        dialog.findViewById(R.id.btn_music_dlg_close).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dialog.dismiss();
                setImmersiveMode();
            }
        });

        View.OnClickListener musicChoiceListener = new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String pkg = "";
                String name = "";
                int id = v.getId();
                if (id == R.id.btn_play_oem_music) {
                    pkg = "com.chinatsp.music";
                    name = "Música OEM Changan";
                } else if (id == R.id.btn_play_smarttube) {
                    pkg = getFirstInstalled("org.smarttube.stable", "com.teamsmart.videomanager.tv", "com.liskovsoft.videomanager");
                    name = "SmartTube Pro";
                } else if (id == R.id.btn_play_newpipe) {
                    pkg = "org.schabi.newpipe";
                    name = "NewPipe";
                } else if (id == R.id.btn_play_spotify) {
                    pkg = getFirstInstalled("com.maxrave.simpmusic", "oss.krtirtho.spotube", "com.spotify.music");
                    name = "SimpMusic Hi-Fi";
                } else if (id == R.id.btn_play_rimusic) {
                    pkg = getFirstInstalled("com.maxrave.simpmusic", "it.fast4x.rimusic");
                    name = "SimpMusic / RiMusic";
                }

                if (cbRemember != null && cbRemember.isChecked() && !pkg.isEmpty()) {
                    prefs.edit().putString(KEY_DEFAULT_MUSIC, pkg).apply();
                    Toast.makeText(MainActivity.this, name + " fijado como reproductor predeterminado", Toast.LENGTH_SHORT).show();
                }

                dialog.dismiss();
                if (!pkg.isEmpty()) {
                    launchAppOrToast(pkg, name);
                } else {
                    Toast.makeText(MainActivity.this, "Iniciando: " + name, Toast.LENGTH_SHORT).show();
                }
            }
        };

        dialog.findViewById(R.id.btn_play_oem_music).setOnClickListener(musicChoiceListener);
        dialog.findViewById(R.id.btn_play_smarttube).setOnClickListener(musicChoiceListener);
        dialog.findViewById(R.id.btn_play_newpipe).setOnClickListener(musicChoiceListener);
        dialog.findViewById(R.id.btn_play_spotify).setOnClickListener(musicChoiceListener);
        dialog.findViewById(R.id.btn_play_rimusic).setOnClickListener(musicChoiceListener);

        dialog.show();
    }

    private String getFirstInstalled(String... packages) {
        PackageManager pm = getPackageManager();
        for (String p : packages) {
            try {
                pm.getPackageInfo(p, 0);
                return p;
            } catch (Exception ignored) {}
        }
        return packages[0];
    }

    // ========================================================================
    // 8. QUICK CHANGAN CONTROL DIALOG (DRIVE MODE MEMORY, 360, NIGHT, FACTORY)
    // ========================================================================
    private void showQuickControlDialog() {
        final Dialog dialog = new Dialog(this, android.R.style.Theme_NoTitleBar_Fullscreen);
        dialog.setContentView(R.layout.dialog_changan_control);
        setDialogImmersive(dialog);

        dialog.findViewById(R.id.btn_ctrl_close).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dialog.dismiss();
                setImmersiveMode();
            }
        });

        // 1. Modos de manejo (Guardado en memoria)
        View.OnClickListener modeListener = new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String modeName = "CONFORT";
                int id = v.getId();
                if (id == R.id.btn_mode_eco) modeName = "ECO";
                else if (id == R.id.btn_mode_sport) modeName = "SPORT";

                prefs.edit().putString(KEY_DRIVE_MODE, modeName).apply();
                Toast.makeText(MainActivity.this, "Modo " + modeName + " guardado en memoria", Toast.LENGTH_SHORT).show();

                // Lanza control vehicular OEM
                launchVehicle();
                dialog.dismiss();
            }
        };

        dialog.findViewById(R.id.btn_mode_eco).setOnClickListener(modeListener);
        dialog.findViewById(R.id.btn_mode_comfort).setOnClickListener(modeListener);
        dialog.findViewById(R.id.btn_mode_sport).setOnClickListener(modeListener);

        // 2. Herramientas
        dialog.findViewById(R.id.btn_ctrl_camera360).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dialog.dismiss();
                launchCamera();
            }
        });

        dialog.findViewById(R.id.btn_ctrl_night_mode).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dialog.dismiss();
                activateNightMode();
            }
        });

        dialog.findViewById(R.id.btn_ctrl_eq).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dialog.dismiss();
                launchExplicit("com.chinatsp.settings", "com.chinatsp.settings.sound.SoundActivity", "Ajustes de Sonido Changan");
            }
        });

        dialog.findViewById(R.id.btn_ctrl_factory_launcher).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dialog.dismiss();
                launchFactory();
            }
        });

        dialog.show();
    }

    private void setDialogImmersive(Dialog dialog) {
        Window window = dialog.getWindow();
        if (window != null) {
            window.getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            );
        }
    }

    // ========================================================================
    // 9. REAL CAR OEM FUNCTIONS & INTENTS
    // ========================================================================
    private void launchClimate() {
        Intent intent = getPackageManager().getLaunchIntentForPackage("com.os.airconditioner");
        if (intent != null) {
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        } else {
            launchExplicit("com.os.airconditioner", "com.os.airconditioner.MainActivity", "Climatizador A/C");
        }
    }

    private void launchRadio() {
        // Actualizar widget de musica instantaneamente a Radio Changan
        if (tvTrackStatus != null) tvTrackStatus.setText("Radio FM/AM");
        if (tvTrackTitle != null) tvTrackTitle.setText("Sintonizador Changan");
        if (tvTrackArtist != null) tvTrackArtist.setText("Transmisión en vivo");
        if (ivAlbumArt != null) ivAlbumArt.setImageResource(R.drawable.ic_fav_radio);

        // 1. Broadcasts de activación de radio OEM Changan / CoAgent
        try {
            sendBroadcast(new Intent("com.coagent.intent.action.Mode_RADIO"));
            sendBroadcast(new Intent("com.chinatsp.action.RADIO"));
            sendBroadcast(new Intent("com.chinatsp.radio.action.play"));
            sendBroadcast(new Intent("com.chinatsp.music.remote.local.radio"));
        } catch (Exception ignored) {}

        // 2. Radio OEM Oficial Changan X7 Plus (eDog Oushang SDK & ChinaTSP Radio)
        try {
            Intent pmIntent = getPackageManager().getLaunchIntentForPackage("com.edog.car.changanoushangsdk");
            if (pmIntent != null) {
                pmIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(pmIntent);
                return;
            }
        } catch (Exception ignored) {}

        String[][] explicitRadio = {
            {"com.edog.car.changanoushangsdk", "com.edog.car.oushangsdk.activity.main.MainActivity"},
            {"com.edog.car.oushangsdk", "com.edog.car.oushangsdk.activity.main.MainActivity"},
            {"net.programmierecke.radiodroid2", "net.programmierecke.radiodroid2.ui.MainActivity"},
            {"com.chinatsp.radio", "com.chinatsp.radio.MainActivity"},
            {"com.chinatsp.radio", "com.chinatsp.radio.RadioActivity"},
            {"com.chinatsp.radio", "com.chinatsp.radio.ui.MainActivity"},
            {"com.chinatsp.fmradio", "com.chinatsp.fmradio.MainActivity"},
            {"com.chinatsp.music", "com.chinatsp.music.BtMusicPlay"},
            {"com.os.radio", "com.os.radio.MainActivity"},
            {"com.android.fmradio", "com.android.fmradio.FmMainActivity"}
        };
        for (String[] target : explicitRadio) {
            try {
                Intent exp = new Intent();
                exp.setComponent(new ComponentName(target[0], target[1]));
                exp.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED);
                startActivity(exp);
                return;
            } catch (Exception ignored) {}
        }

        // 3. Servicio de control de radio OEM
        try {
            Intent svc = new Intent();
            svc.setComponent(new ComponentName("com.chinatsp.radio", "com.chinatsp.radio.service.PlayControlService"));
            startService(svc);
        } catch (Exception ignored) {}

        // 4. Intent con ACTION_MAIN para com.chinatsp.radio o com.edog.car
        String[] radioPackages = {
            "com.edog.car.oushangsdk",
            "com.edog.car.changanoushangsdk",
            "com.chinatsp.radio",
            "com.chinatsp.fmradio",
            "com.os.radio",
            "com.android.fmradio"
        };
        for (String pkg : radioPackages) {
            try {
                Intent radioIntent = new Intent(Intent.ACTION_MAIN);
                radioIntent.setPackage(pkg);
                List<ResolveInfo> list = getPackageManager().queryIntentActivities(radioIntent, 0);
                if (list != null && !list.isEmpty()) {
                    Intent intent = new Intent();
                    intent.setComponent(new ComponentName(pkg, list.get(0).activityInfo.name));
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED);
                    startActivity(intent);
                    return;
                }
            } catch (Exception ignored) {}

            Intent intent = getPackageManager().getLaunchIntentForPackage(pkg);
            if (intent != null) {
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(intent);
                return;
            }
        }
        Toast.makeText(this, "Radio FM/AM Changan", Toast.LENGTH_SHORT).show();
    }

    private void launchNavigation() {
        String savedNav = prefs.getString("default_nav_package", "");
        if (!savedNav.isEmpty()) {
            applyFullscreenBypass(savedNav);
            Intent intent = getPackageManager().getLaunchIntentForPackage(savedNav);
            if (intent != null) {
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(intent);
                return;
            }
        }

        String[] navPackages = {
            "com.waze",
            "com.andrerinas.headunitrevived",
            "gb.xxy.hr",
            "cn.manstep.phonemirrorBox",
            "com.carlinkit.autokit",
            "com.zjinnova.zlink",
            "com.autonavi.amapauto",
            "com.generalmagic.magicearth",
            "com.google.android.apps.maps"
        };
        for (String pkg : navPackages) {
            Intent intent = getPackageManager().getLaunchIntentForPackage(pkg);
            if (intent != null) {
                applyFullscreenBypass(pkg);
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(intent);
                return;
            }
        }
        showNavSelectorDialog();
    }

    private void showNavSelectorDialog() {
        final Dialog dialog = new Dialog(this, android.R.style.Theme_NoTitleBar_Fullscreen);
        dialog.setContentView(R.layout.dialog_nav_selector);
        setDialogImmersive(dialog);

        View closeBtn = dialog.findViewById(R.id.btn_close_nav_dlg);
        if (closeBtn != null) {
            closeBtn.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) { dialog.dismiss(); setImmersiveMode(); }
            });
        }

        View.OnClickListener pickNav = new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String pkg = "";
                String name = "";
                int id = v.getId();
                if (id == R.id.btn_nav_pick_headunit) {
                    pkg = getFirstInstalled("com.andrerinas.headunitrevived", "gb.xxy.hr");
                    name = "Headunit Reloaded";
                } else if (id == R.id.btn_nav_pick_autokit) {
                    pkg = getFirstInstalled("cn.manstep.phonemirrorBox", "com.carlinkit.autokit", "com.zjinnova.zlink");
                    name = "AutoKit";
                } else if (id == R.id.btn_nav_pick_waze) {
                    pkg = "com.waze";
                    name = "Waze";
                } else if (id == R.id.btn_nav_pick_maps) {
                    pkg = "com.google.android.apps.maps";
                    name = "Google Maps";
                }

                if (!pkg.isEmpty()) {
                    prefs.edit().putString("default_nav_package", pkg).putString("default_nav_name", name).apply();
                    TextView tvSub = findViewById(R.id.tv_nav_subtitle);
                    if (tvSub != null) tvSub.setText(name);
                    Toast.makeText(MainActivity.this, "✓ " + name + " establecido como navegador predeterminado", Toast.LENGTH_SHORT).show();
                    launchAppOrToast(pkg, name);
                }
                dialog.dismiss();
            }
        };

        View bHu = dialog.findViewById(R.id.btn_nav_pick_headunit);
        if (bHu != null) bHu.setOnClickListener(pickNav);
        View bAk = dialog.findViewById(R.id.btn_nav_pick_autokit);
        if (bAk != null) bAk.setOnClickListener(pickNav);
        View bWz = dialog.findViewById(R.id.btn_nav_pick_waze);
        if (bWz != null) bWz.setOnClickListener(pickNav);
        View bMp = dialog.findViewById(R.id.btn_nav_pick_maps);
        if (bMp != null) bMp.setOnClickListener(pickNav);

        dialog.show();
    }

    private void launchPhone() {
        String[] phonePackages = {
            "com.chinatsp.phone",
            "com.incall.apps.btphone",
            "com.android.dialer"
        };
        for (String pkg : phonePackages) {
            Intent intent = getPackageManager().getLaunchIntentForPackage(pkg);
            if (intent != null) {
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(intent);
                return;
            }
        }
        launchExplicit("com.chinatsp.phone", "com.chinatsp.phone.MainActivity", "Teléfono Bluetooth");
    }

    private void launchCamera() {
        // Enlaza de forma directa y sincronizada con el HardwareKeyReceiver
        // Ejecuta la misma lógica que el botón físico del timón
        HardwareKeyReceiver.triggerAvm360(this);
    }

    private void showCameraSelectorDialog() {
        final Dialog dialog = new Dialog(this, android.R.style.Theme_NoTitleBar_Fullscreen);
        dialog.setContentView(R.layout.dialog_camera_selector);
        setDialogImmersive(dialog);

        View closeBtn = dialog.findViewById(R.id.btn_close_cam_dlg);
        if (closeBtn != null) {
            closeBtn.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) { dialog.dismiss(); setImmersiveMode(); }
            });
        }

        // 1. AVM Live
        View btnTestAvm = dialog.findViewById(R.id.btn_test_cam_avmlive);
        if (btnTestAvm != null) {
            btnTestAvm.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) {
                    testCameraComponent("com.chinatsp.avmlive", "com.chinatsp.avmlive.MainActivity");
                }
            });
        }
        View btnSaveAvm = dialog.findViewById(R.id.btn_save_cam_avmlive);
        if (btnSaveAvm != null) {
            btnSaveAvm.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) {
                    prefs.edit()
                        .putString("pref_camera_pkg", "com.chinatsp.avmlive")
                        .putString("pref_camera_cls", "com.chinatsp.avmlive.MainActivity")
                        .apply();
                    Toast.makeText(MainActivity.this, "✓ Guardado: Cámara AVM Live 360° asignada al botón y timón", Toast.LENGTH_LONG).show();
                    dialog.dismiss();
                }
            });
        }

        // 2. Builtin HD Camera
        View btnTestHd = dialog.findViewById(R.id.btn_test_cam_hd);
        if (btnTestHd != null) {
            btnTestHd.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) {
                    testCameraComponent("com.chinatsp.dvrcamera", "com.chinatsp.dvrcamera.builtin.hdcamera.BuiltinHDCameraActivity");
                }
            });
        }
        View btnSaveHd = dialog.findViewById(R.id.btn_save_cam_hd);
        if (btnSaveHd != null) {
            btnSaveHd.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) {
                    prefs.edit()
                        .putString("pref_camera_pkg", "com.chinatsp.dvrcamera")
                        .putString("pref_camera_cls", "com.chinatsp.dvrcamera.builtin.hdcamera.BuiltinHDCameraActivity")
                        .apply();
                    Toast.makeText(MainActivity.this, "✓ Guardado: HD Camera asignada", Toast.LENGTH_LONG).show();
                    dialog.dismiss();
                }
            });
        }

        // 3. Broadcasts OEM
        View btnTestBc = dialog.findViewById(R.id.btn_test_cam_broadcast);
        if (btnTestBc != null) {
            btnTestBc.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) {
                    triggerAvm360Broadcasts();
                    Toast.makeText(MainActivity.this, "Disparando señal CAN Bus AVM_ON...", Toast.LENGTH_SHORT).show();
                }
            });
        }
        View btnSaveBc = dialog.findViewById(R.id.btn_save_cam_broadcast);
        if (btnSaveBc != null) {
            btnSaveBc.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) {
                    prefs.edit()
                        .putString("pref_camera_pkg", "OEM_BROADCAST")
                        .putString("pref_camera_cls", "OEM_BROADCAST")
                        .apply();
                    Toast.makeText(MainActivity.this, "✓ Guardado: Disparo directo CAN Bus AVM_ON", Toast.LENGTH_LONG).show();
                    dialog.dismiss();
                }
            });
        }

        dialog.show();
    }

    private void testCameraComponent(String pkg, String cls) {
        try {
            Intent intent = new Intent();
            intent.setComponent(new ComponentName(pkg, cls));
            intent.setAction(Intent.ACTION_MAIN);
            intent.addCategory(Intent.CATEGORY_LAUNCHER);
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED);
            startActivity(intent);
        } catch (Exception e) {
            Intent launch = getPackageManager().getLaunchIntentForPackage(pkg);
            if (launch != null) {
                launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(launch);
            } else {
                Toast.makeText(this, "Paquete no disponible: " + pkg, Toast.LENGTH_SHORT).show();
            }
        }
    }

    // ========================================================================
    // ASISTENTE DE CONEXIÓN MULTI-ESCENARIO ANDROID AUTO / HEADUNIT RELOADED
    // ========================================================================
    private void launchHeadunit() {
        String savedIp = prefs.getString("headunit_target_ip", "192.168.43.1");
        launchHeadunitWithIp(savedIp);
    }

    private void launchHeadunitWithIp(String ip) {
        String[] huPackages = {"com.andrerinas.headunitrevived", "gb.xxy.hr"};
        for (String pkg : huPackages) {
            Intent intent = getPackageManager().getLaunchIntentForPackage(pkg);
            if (intent != null) {
                applyFullscreenBypass(pkg);
                intent.putExtra("ip", ip);
                intent.putExtra("port", 5277);
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                try {
                    Intent wifiBc = new Intent("gb.xxy.hr.WIFI_CONNECT");
                    wifiBc.putExtra("ip", ip);
                    wifiBc.putExtra("port", 5277);
                    sendBroadcast(wifiBc);
                } catch (Exception ignored) {}
                startActivity(intent);
                Toast.makeText(this, "Conectando Android Auto a " + ip + ":5277", Toast.LENGTH_SHORT).show();
                return;
            }
        }
        showHeadunitConnectDialog();
    }

    private void launchHeadunitUsbMode() {
        try {
            Intent intent = new Intent();
            intent.setComponent(new ComponentName("com.andrerinas.headunitrevived", "com.andrerinas.headunitrevived.UsbAccessoryActivity"));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        } catch (Exception e) {
            launchHeadunit();
        }
    }

    private void launchHeadunitStandalone() {
        try {
            Intent intent = new Intent();
            intent.setComponent(new ComponentName("com.andrerinas.headunitrevived", "com.andrerinas.headunitrevived.SelfModeActivity"));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        } catch (Exception e) {
            launchHeadunit();
        }
    }

    private void showHeadunitConnectDialog() {
        final Dialog dialog = new Dialog(this, android.R.style.Theme_NoTitleBar_Fullscreen);
        dialog.setContentView(R.layout.dialog_headunit_connect);
        setDialogImmersive(dialog);

        View closeBtn = dialog.findViewById(R.id.btn_close_headunit_dlg);
        if (closeBtn != null) {
            closeBtn.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) { dialog.dismiss(); setImmersiveMode(); }
            });
        }

        TextView tvIp = dialog.findViewById(R.id.tv_hu_current_ip);
        final String localIp = getWifiIpAddress();
        if (tvIp != null) {
            tvIp.setText("IP Local del Auto: " + localIp);
        }

        final android.widget.EditText etPhoneIp = dialog.findViewById(R.id.et_phone_ip);
        String savedIp = prefs.getString("headunit_target_ip", "192.168.43.1");
        if (etPhoneIp != null) {
            etPhoneIp.setText(savedIp);
        }

        // Modo 1: Hotspot directo (Gateway 192.168.43.1)
        View btnHotspot = dialog.findViewById(R.id.btn_hu_mode_hotspot);
        if (btnHotspot != null) {
            btnHotspot.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) {
                    launchHeadunitWithIp("192.168.43.1");
                    dialog.dismiss();
                }
            });
        }

        // Modo 2: IP personalizada (3er móvil como router)
        View btnConnectIp = dialog.findViewById(R.id.btn_connect_custom_ip);
        if (btnConnectIp != null) {
            btnConnectIp.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) {
                    String targetIp = etPhoneIp != null ? etPhoneIp.getText().toString().trim() : "";
                    if (targetIp.isEmpty()) {
                        Toast.makeText(MainActivity.this, "Ingresa una dirección IP válida", Toast.LENGTH_SHORT).show();
                        return;
                    }
                    prefs.edit().putString("headunit_target_ip", targetIp).apply();
                    launchHeadunitWithIp(targetIp);
                    dialog.dismiss();
                }
            });
        }

        // Escanear / Detectar Subred
        View btnScan = dialog.findViewById(R.id.btn_scan_subnet_ip);
        if (btnScan != null) {
            btnScan.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) {
                    String detectedSubnet = "192.168.43.";
                    if (localIp.contains(".")) {
                        int lastDot = localIp.lastIndexOf('.');
                        detectedSubnet = localIp.substring(0, lastDot + 1);
                    }
                    if (etPhoneIp != null) {
                        etPhoneIp.setText(detectedSubnet + "2");
                        Toast.makeText(MainActivity.this, "Subred detectada: " + detectedSubnet + "*", Toast.LENGTH_SHORT).show();
                    }
                }
            });
        }

        // Modo 3: Cable USB
        View btnUsb = dialog.findViewById(R.id.btn_hu_mode_usb);
        if (btnUsb != null) {
            btnUsb.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) {
                    launchHeadunitUsbMode();
                    dialog.dismiss();
                }
            });
        }

        // Modo 4: Modo Autónomo
        View btnStandalone = dialog.findViewById(R.id.btn_hu_mode_standalone);
        if (btnStandalone != null) {
            btnStandalone.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) {
                    launchHeadunitStandalone();
                    dialog.dismiss();
                }
            });
        }

        dialog.show();
    }

    private void setChanganAvmHardwareProperty(boolean open) {
        // Metodo 1: Reflection sobre android.car.Car y CarCabinManager
        try {
            Class<?> carClass = Class.forName("android.car.Car");
            java.lang.reflect.Method createCar = carClass.getMethod("createCar", Context.class);
            Object carObj = createCar.invoke(null, this);
            if (carObj != null) {
                java.lang.reflect.Method getCarManager = carClass.getMethod("getCarManager", String.class);
                Object cabinMgr = getCarManager.invoke(carObj, "cabin");
                if (cabinMgr != null) {
                    java.lang.reflect.Method setIntProp = cabinMgr.getClass().getMethod("setIntProperty", int.class, int.class, int.class);
                    setIntProp.invoke(cabinMgr, 0x2140eeb4, 0, open ? 1 : 0);
                    android.util.Log.i("LauncherX7", "CarCabinManager.setIntProperty(0x2140eeb4, 0, 1) ejecutado con exito.");
                }
            }
        } catch (Throwable t) {
            android.util.Log.w("LauncherX7", "Reflection CarCabinManager: " + t.getMessage());
        }

        // Metodo 2: CarCabinManagerUtil propietario si esta presente en el classpath
        try {
            Class<?> utilClass = Class.forName("com.chinatsp.launcher.utils.CarCabinManagerUtil");
            java.lang.reflect.Method getInstance = utilClass.getMethod("getInstance", Context.class);
            Object util = getInstance.invoke(null, getApplicationContext());
            if (util != null) {
                java.lang.reflect.Method setIntProp = utilClass.getMethod("setIntProperty", int.class, int.class, int.class);
                setIntProp.invoke(util, 0x2140eeb4, 0, open ? 1 : 0);
            }
        } catch (Throwable ignored) {}
    }

    private void triggerAvm360Broadcasts() {
        try {
            sendBroadcast(new Intent("com.chinatsp.action.AVM_ON"));
            sendBroadcast(new Intent("com.chinatsp.action.AVM_DISPLAY_SWITCH"));
            sendBroadcast(new Intent("com.chinatsp.tspcamera.service.BootService.TSPCAMERA"));
            sendBroadcast(new Intent("changan.os.action.to.user.center.view.fullsrceen"));
            Intent openVc = new Intent("open_vc_from_others");
            openVc.putExtra("open_vc", "full_view");
            openVc.putExtra("vc_type", 1);
            sendBroadcast(openVc);
            sendBroadcast(new Intent("com.chinatsp.action.ENTER_AVM"));
            sendBroadcast(new Intent("com.chinatsp.systemui.ACTION_ENTER_AVM"));
            sendBroadcast(new Intent("com.chinatsp.systemui.ACTION_AVM_DISPLAY_SWITCH"));
        } catch (Exception ignored) {}
    }

    private void launchVehicle() {
        String[] vehiclePackages = {
            "com.chinatsp.vehiclecontrol",
            "com.chinatsp.tfactoryapp",
            "com.android.settings"
        };
        for (String pkg : vehiclePackages) {
            Intent intent = getPackageManager().getLaunchIntentForPackage(pkg);
            if (intent != null) {
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(intent);
                return;
            }
        }
        launchExplicit("com.chinatsp.vehiclecontrol", "com.chinatsp.vehiclecontrol.main.MainActivity", "Control Vehículo");
    }

    private void launchFactory() {
        try {
            Intent factoryIntent = new Intent();
            factoryIntent.setComponent(new ComponentName("com.chinatsp.launcher", "com.chinatsp.launcher.MainAct"));
            factoryIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED);
            startActivity(factoryIntent);
        } catch (Exception e) {
            Intent intent = getPackageManager().getLaunchIntentForPackage("com.chinatsp.launcher");
            if (intent != null) {
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(intent);
            } else {
                Toast.makeText(this, "Launcher Original OnStyle Fábrica", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void launchSettings() {
        Intent intent = getPackageManager().getLaunchIntentForPackage("com.chinatsp.settings");
        if (intent != null) {
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        } else {
            try {
                Intent sIntent = new Intent(android.provider.Settings.ACTION_SETTINGS);
                sIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(sIntent);
            } catch (Exception e) {
                Toast.makeText(this, "Ajustes", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void applyFullscreenBypass(String packageName) {
        if (packageName == null || packageName.isEmpty()) return;
        try {
            Intent info = new Intent("com.chinatsp.systemui.ACTION_APP_INFO");
            info.putExtra("packageName", packageName);
            info.putExtra("appCentered", 2);
            sendBroadcast(info);

            Intent hideBar = new Intent("com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR");
            hideBar.putExtra("packageName", packageName);
            sendBroadcast(hideBar);

            sendBroadcast(new Intent("com.chinatsp.action.ACTION_ENTER_FULLSCREEN"));
        } catch (Exception ignored) {}
    }

    private void launchAppOrToast(String packageName, String name) {
        applyFullscreenBypass(packageName);
        Intent intent = getPackageManager().getLaunchIntentForPackage(packageName);
        if (intent != null) {
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        } else {
            Toast.makeText(this, "Iniciando: " + name, Toast.LENGTH_SHORT).show();
        }
    }

    private void launchExplicit(String packageName, String activityName, String fallbackLabel) {
        try {
            Intent intent = new Intent();
            intent.setComponent(new ComponentName(packageName, activityName));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        } catch (Exception e) {
            Intent launch = getPackageManager().getLaunchIntentForPackage(packageName);
            if (launch != null) {
                launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(launch);
            } else {
                Toast.makeText(this, fallbackLabel, Toast.LENGTH_SHORT).show();
            }
        }
    }


    // ========================================================================
    // SECOND HOME & VIEWFLIPPER GESTURES
    // ========================================================================
    private void setupPageGestures() {
        viewFlipper = findViewById(R.id.view_flipper_home);
        dotPage1 = findViewById(R.id.dot_page1);
        dotPage2 = findViewById(R.id.dot_page2);

        if (dotPage1 != null) {
            dotPage1.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) { showPage(0); }
            });
        }
        if (dotPage2 != null) {
            dotPage2.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) { showPage(1); }
            });
        }

        gestureDetector = new GestureDetector(this, new GestureDetector.SimpleOnGestureListener() {
            @Override
            public boolean onFling(MotionEvent e1, MotionEvent e2, float velocityX, float velocityY) {
                if (e1 == null || e2 == null) return false;
                float diffX = e2.getX() - e1.getX();
                float diffY = e2.getY() - e1.getY();
                if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 80 && Math.abs(velocityX) > 100) {
                    if (diffX < 0) {
                        showPage(1); // Swipe izquierda -> Pagina 2
                    } else {
                        showPage(0); // Swipe derecha -> Pagina 1
                    }
                    return true;
                }
                return false;
            }
        });

        setupSecondHomeGrid();
    }

    private void showPage(int page) {
        if (viewFlipper == null) return;
        int current = viewFlipper.getDisplayedChild();
        if (current == page) return;

        if (page == 1) {
            viewFlipper.setInAnimation(this, android.R.anim.slide_in_left);
            viewFlipper.setOutAnimation(this, android.R.anim.slide_out_right);
            viewFlipper.setDisplayedChild(1);
        } else {
            viewFlipper.setInAnimation(this, android.R.anim.slide_in_left);
            viewFlipper.setOutAnimation(this, android.R.anim.slide_out_right);
            viewFlipper.setDisplayedChild(0);
        }
        updatePageDots(page);
        setImmersiveMode();
    }

    private void updatePageDots(int page) {
        if (dotPage1 != null) {
            dotPage1.setBackgroundResource(page == 0 ? R.drawable.bg_indicator_active : R.drawable.bg_indicator_inactive);
        }
        if (dotPage2 != null) {
            dotPage2.setBackgroundResource(page == 1 ? R.drawable.bg_indicator_active : R.drawable.bg_indicator_inactive);
        }
    }

    private void setupSecondHomeGrid() {
        gvSecondHome = findViewById(R.id.gv_second_home);
        if (gvSecondHome == null) return;

        final PackageManager pm = getPackageManager();
        Intent mainIntent = new Intent(Intent.ACTION_MAIN, null);
        mainIntent.addCategory(Intent.CATEGORY_LAUNCHER);
        final List<ResolveInfo> appList = pm.queryIntentActivities(mainIntent, 0);

        Collections.sort(appList, new Comparator<ResolveInfo>() {
            @Override
            public int compare(ResolveInfo a, ResolveInfo b) {
                CharSequence l1 = a.loadLabel(pm);
                CharSequence l2 = b.loadLabel(pm);
                return (l1 != null ? l1.toString() : "").compareToIgnoreCase(l2 != null ? l2.toString() : "");
            }
        });

        gvSecondHome.setAdapter(new BaseAdapter() {
            @Override public int getCount() { return appList.size(); }
            @Override public Object getItem(int position) { return appList.get(position); }
            @Override public long getItemId(int position) { return position; }

            @Override
            public View getView(int position, View convertView, ViewGroup parent) {
                if (convertView == null) {
                    convertView = getLayoutInflater().inflate(R.layout.item_app_drawer, parent, false);
                }
                ResolveInfo info = appList.get(position);
                ImageView iv = convertView.findViewById(R.id.iv_app_icon);
                TextView tv = convertView.findViewById(R.id.tv_app_label);

                if (iv != null) {
                    iv.setImageDrawable(loadRobustAppIcon(info, pm));
                }
                if (tv != null) {
                    CharSequence label = info.loadLabel(pm);
                    tv.setText(label != null ? label : info.activityInfo.name);
                }
                return convertView;
            }
        });

        gvSecondHome.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                ResolveInfo info = appList.get(position);
                String pkg = info.activityInfo.packageName;
                applyFullscreenBypass(pkg);
                Intent launchIntent = pm.getLaunchIntentForPackage(pkg);
                if (launchIntent != null) {
                    launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    startActivity(launchIntent);
                }
            }
        });
    }

    // ========================================================================
    // ZERO BLANK ICONS - ROBUST AUTOMOTIVE ICON LOADER
    // ========================================================================
    private Drawable loadRobustAppIcon(ResolveInfo info, PackageManager pm) {
        if (info == null || info.activityInfo == null) {
            return getResources().getDrawable(R.drawable.ic_apps);
        }

        // 1. CARGAR PRIMERO EL ICONO NATIVO ORIGINAL DE LA APLICACIÓN
        try {
            Drawable nativeIcon = info.loadIcon(pm);
            if (nativeIcon != null) {
                Drawable defIcon = pm.getDefaultActivityIcon();
                if (defIcon == null || nativeIcon.getConstantState() == null 
                        || !nativeIcon.getConstantState().equals(defIcon.getConstantState())) {
                    return nativeIcon; // Icono nativo oficial preservado al 100%
                }
            }
        } catch (Throwable ignored) {}

        String pkg = info.activityInfo.packageName.toLowerCase();

        // 1. Iconos dedicados de alta definicion
        if (pkg.contains("waze")) {
            try { return getResources().getDrawable(R.drawable.icon_waze); } catch (Exception ignored) {}
        }
        if (pkg.contains("brave")) {
            try { return getResources().getDrawable(R.drawable.icon_brave); } catch (Exception ignored) {}
        }
        if (pkg.contains("x7plus.launcher") || pkg.contains("cockpit")) {
            try { return getResources().getDrawable(R.drawable.ic_launcher); } catch (Exception ignored) {}
        }
        if (pkg.contains("camera") || pkg.contains("dvr")) {
            try { return getResources().getDrawable(R.drawable.card_camera); } catch (Exception ignored) {}
        }
        if (pkg.contains("music") || pkg.contains("innertune") || pkg.contains("rimusic") || pkg.contains("vimusic")) {
            try { return getResources().getDrawable(R.drawable.ic_fav_music); } catch (Exception ignored) {}
        }
        if (pkg.contains("radio")) {
            try { return getResources().getDrawable(R.drawable.ic_fav_radio); } catch (Exception ignored) {}
        }
        if (pkg.contains("phone") || pkg.contains("btphone")) {
            try { return getResources().getDrawable(R.drawable.ic_fav_phone); } catch (Exception ignored) {}
        }
        if (pkg.contains("setting") || pkg.contains("config")) {
            try { return getResources().getDrawable(R.drawable.ic_side_settings); } catch (Exception ignored) {}
        }
        if (pkg.contains("carauto") || pkg.contains("autokit") || pkg.contains("headunit") || pkg.contains("phonemirror")) {
            try { return getResources().getDrawable(R.drawable.ic_side_nav); } catch (Exception ignored) {}
        }
        if (pkg.contains("vehicle") || pkg.contains("aircon") || pkg.contains("climate")) {
            try { return getResources().getDrawable(R.drawable.card_car); } catch (Exception ignored) {}
        }
        if (pkg.contains("cloudstream") || pkg.contains("smarttube") || pkg.contains("newpipe") || pkg.contains("youtube") || pkg.contains("tv")) {
            try { return getResources().getDrawable(R.drawable.ic_side_apps); } catch (Exception ignored) {}
        }

        // 2. Extraccion estandar de PackageManager
        Drawable icon = null;
        try {
            icon = info.loadIcon(pm);
        } catch (Exception ignored) {}
        if (icon == null) {
            try {
                icon = info.activityInfo.loadIcon(pm);
            } catch (Exception ignored) {}
        }
        if (icon == null) {
            try {
                icon = pm.getApplicationIcon(info.activityInfo.packageName);
            } catch (Exception ignored) {}
        }

        // 3. Validar dimensiones intrinsecas
        if (icon != null && icon.getIntrinsicWidth() > 0 && icon.getIntrinsicHeight() > 0) {
            return icon;
        }

        // 4. Badge automotriz titanio/cian garantizado (CERO ICONOS EN BLANCO)
        CharSequence label = null;
        try {
            label = info.loadLabel(pm);
        } catch (Exception ignored) {}
        String labelStr = (label != null && label.length() > 0) ? label.toString() : info.activityInfo.name;
        return createAutomotiveBadge(labelStr);
    }

    private Drawable createAutomotiveBadge(String label) {
        int size = 112;
        Bitmap bmp = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(bmp);

        // Fondo degradado titanio oscuro
        Paint bgPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        bgPaint.setColor(Color.parseColor("#131D2E"));
        RectF rect = new RectF(4, 4, size - 4, size - 4);
        canvas.drawRoundRect(rect, 22, 22, bgPaint);

        // Borde neon cian sutil
        Paint borderPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        borderPaint.setStyle(Paint.Style.STROKE);
        borderPaint.setStrokeWidth(3f);
        borderPaint.setColor(Color.parseColor("#38BDF8"));
        canvas.drawRoundRect(rect, 22, 22, borderPaint);

        // Iniciales
        String initials = "APP";
        if (label != null && !label.trim().isEmpty()) {
            String[] words = label.trim().split("\\s+");
            if (words.length >= 2 && words[0].length() > 0 && words[1].length() > 0) {
                initials = ("" + words[0].charAt(0) + words[1].charAt(0)).toUpperCase();
            } else if (words[0].length() >= 2) {
                initials = words[0].substring(0, Math.min(2, words[0].length())).toUpperCase();
            } else {
                initials = words[0].toUpperCase();
            }
        }

        Paint textPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        textPaint.setColor(Color.parseColor("#FFFFFF"));
        textPaint.setTextSize(34f);
        textPaint.setTypeface(Typeface.create(Typeface.DEFAULT, Typeface.BOLD));
        textPaint.setTextAlign(Paint.Align.CENTER);

        Paint.FontMetrics fm = textPaint.getFontMetrics();
        float y = (size / 2f) - ((fm.descent + fm.ascent) / 2f);
        canvas.drawText(initials, size / 2f, y, textPaint);

        return new BitmapDrawable(getResources(), bmp);
    }

    // ========================================================================
    // 10. APPLICATION DRAWER
    // ========================================================================
    private void showAppDrawer() {
        final Dialog dialog = new Dialog(this, android.R.style.Theme_NoTitleBar_Fullscreen);
        dialog.setContentView(R.layout.dialog_app_drawer);
        setDialogImmersive(dialog);

        GridView gv = dialog.findViewById(R.id.gv_apps);
        Button btnFactory = dialog.findViewById(R.id.btn_drawer_factory);
        ImageButton btnClose = dialog.findViewById(R.id.btn_drawer_close);

        if (btnFactory != null) {
            btnFactory.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    dialog.dismiss();
                    launchFactory();
                }
            });
        }

        if (btnClose != null) {
            btnClose.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    dialog.dismiss();
                    setImmersiveMode();
                }
            });
        }

        final PackageManager pm = getPackageManager();
        Intent mainIntent = new Intent(Intent.ACTION_MAIN, null);
        mainIntent.addCategory(Intent.CATEGORY_LAUNCHER);
        final List<ResolveInfo> appList = pm.queryIntentActivities(mainIntent, 0);

        Collections.sort(appList, new Comparator<ResolveInfo>() {
            @Override
            public int compare(ResolveInfo a, ResolveInfo b) {
                CharSequence l1 = a.loadLabel(pm);
                CharSequence l2 = b.loadLabel(pm);
                return (l1 != null ? l1.toString() : "").compareToIgnoreCase(l2 != null ? l2.toString() : "");
            }
        });

        if (gv != null) {
            gv.setAdapter(new BaseAdapter() {
                @Override
                public int getCount() {
                    return appList.size();
                }

                @Override
                public Object getItem(int position) {
                    return appList.get(position);
                }

                @Override
                public long getItemId(int position) {
                    return position;
                }

                @Override
                public View getView(int position, View convertView, ViewGroup parent) {
                    if (convertView == null) {
                        convertView = getLayoutInflater().inflate(R.layout.item_app_drawer, parent, false);
                    }
                    ResolveInfo info = appList.get(position);
                    ImageView iv = convertView.findViewById(R.id.iv_app_icon);
                    TextView tv = convertView.findViewById(R.id.tv_app_label);

                    if (iv != null) {
                        iv.setImageDrawable(loadRobustAppIcon(info, pm));
                    }
                    if (tv != null) {
                        CharSequence label = null;
                        try {
                            label = info.loadLabel(pm);
                        } catch (Exception ignored) {}
                        if (label == null || label.length() == 0) {
                            label = info.activityInfo.name;
                        }
                        tv.setText(label);
                    }
                    return convertView;
                }
            });

            gv.setOnItemClickListener(new AdapterView.OnItemClickListener() {
                @Override
                public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                    ResolveInfo info = appList.get(position);
                    String selPkg = info.activityInfo.packageName;
                    applyFullscreenBypass(selPkg);
                    Intent launchIntent = pm.getLaunchIntentForPackage(selPkg);
                    if (launchIntent != null) {
                        launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                        dialog.dismiss();
                        startActivity(launchIntent);
                    }
                }
            });
        }

        dialog.show();
    }

    // ========================================================================
    // 11. AUTOMATIC MOBILE GPS TETHERING & STATUS
    // ========================================================================
    // ========================================================================
    // 11. SUBSISTEMA DE LOCALIZACIÓN SATELITAL HÍBRIDO (NATIVO / MÓVIL)
    // ========================================================================
    private void setupGpsStatus() {
        if (pillGpsStatus != null) {
            pillGpsStatus.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    showGpsStatusDialog();
                }
            });
        }

        MockLocationService.setLocationUpdateListener(new MockLocationService.OnLocationUpdateListener() {
            @Override
            public void onLocationUpdated(final double lat, final double lon, final double speed, final double bearing, final float accuracy) {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        updateGpsStatusUI();
                    }
                });
            }
        });

        updateGpsStatusUI();
    }

    private void updateGpsStatusUI() {
        int mode = MockLocationService.getGpsMode(this);
        if (dotGpsStatus != null) {
            dotGpsStatus.setBackgroundResource(R.drawable.dot_gps_active);
        }
        if (tvGpsStatus != null) {
            tvGpsStatus.setText(mode == MockLocationService.MODE_NATIVE_GPS ? "GPS Satelital" : "GPS Móvil");
        }
    }

    private void updateBluetoothStatusUI() {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                if (tvPhoneBadge == null) {
                    tvPhoneBadge = findViewById(R.id.tv_phone_badge);
                }
                if (tvPhoneBadge == null) return;
                try {
                    BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
                    if (adapter == null || !adapter.isEnabled()) {
                        tvPhoneBadge.setText("DESCONECTADO");
                        tvPhoneBadge.setTextColor(Color.parseColor("#EF4444"));
                        return;
                    }
                    int a2dpState = adapter.getProfileConnectionState(BluetoothProfile.A2DP);
                    int headsetState = adapter.getProfileConnectionState(BluetoothProfile.HEADSET);
                    if (a2dpState == BluetoothProfile.STATE_CONNECTED || headsetState == BluetoothProfile.STATE_CONNECTED) {
                        tvPhoneBadge.setText("CONECTADO");
                        tvPhoneBadge.setTextColor(Color.parseColor("#10B981"));
                    } else if (a2dpState == BluetoothProfile.STATE_CONNECTING || headsetState == BluetoothProfile.STATE_CONNECTING) {
                        tvPhoneBadge.setText("ENLAZANDO");
                        tvPhoneBadge.setTextColor(Color.parseColor("#F59E0B"));
                    } else {
                        tvPhoneBadge.setText("DESCONECTADO");
                        tvPhoneBadge.setTextColor(Color.parseColor("#EF4444"));
                    }
                } catch (Exception e) {
                    tvPhoneBadge.setText("BLUETOOTH");
                    tvPhoneBadge.setTextColor(Color.parseColor("#9CA3AF"));
                }
            }
        });
    }

    private void showGpsStatusDialog() {
        final Dialog dialog = new Dialog(this, android.R.style.Theme_NoTitleBar_Fullscreen);
        dialog.setContentView(R.layout.dialog_gps_status);
        setDialogImmersive(dialog);

        View closeBtn = dialog.findViewById(R.id.btn_close_gps_dlg);
        if (closeBtn != null) {
            closeBtn.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    dialog.dismiss();
                    setImmersiveMode();
                }
            });
        }

        final TextView tvState = dialog.findViewById(R.id.tv_dlg_gps_state);
        final TextView tvCoords = dialog.findViewById(R.id.tv_dlg_gps_coords);
        final View dot = dialog.findViewById(R.id.dlg_dot_gps);
        final Button btnNative = dialog.findViewById(R.id.btn_mode_gps_native);
        final Button btnMock = dialog.findViewById(R.id.btn_mode_gps_mock);
        Button btnReset = dialog.findViewById(R.id.btn_reset_gps_native);

        final Runnable updateDialogUI = new Runnable() {
            @Override
            public void run() {
                int mode = MockLocationService.getGpsMode(MainActivity.this);
                if (btnNative != null) {
                    btnNative.setBackgroundResource(mode == MockLocationService.MODE_NATIVE_GPS ? R.drawable.bg_badge_connected : R.drawable.bg_fav_item);
                }
                if (btnMock != null) {
                    btnMock.setBackgroundResource(mode == MockLocationService.MODE_MOCK_TETHER ? R.drawable.bg_badge_connected : R.drawable.bg_fav_item);
                }
                if (tvState != null) {
                    tvState.setText(mode == MockLocationService.MODE_NATIVE_GPS 
                        ? "Modo Actual: GPS Físico del Auto (Antena Satelital Directa Changan)"
                        : "Modo Actual: GPS Compartido (Tethering UDP 10110 desde Móvil)");
                }
                if (dot != null) {
                    dot.setBackgroundResource(R.drawable.dot_gps_active);
                }
                if (tvCoords != null) {
                    if (MockLocationService.getLastUpdateTime() > 0) {
                        tvCoords.setText(String.format("Últimas coordenadas: %.5f, %.5f (Rumbo: %.1f° | Vel: %.1f km/h)",
                                MockLocationService.getLastLat(), MockLocationService.getLastLon(),
                                MockLocationService.getLastBearing(), MockLocationService.getLastSpeed()));
                    } else {
                        tvCoords.setText("Esperando señal de satélites...");
                    }
                }
                updateGpsStatusUI();
            }
        };

        updateDialogUI.run();

        if (btnNative != null) {
            btnNative.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    MockLocationService.setGpsMode(MainActivity.this, MockLocationService.MODE_NATIVE_GPS);
                    updateDialogUI.run();
                    Toast.makeText(MainActivity.this, "✓ GPS Físico del Auto Activo (Waze y Maps reciben satélites directos)", Toast.LENGTH_LONG).show();
                }
            });
        }

        if (btnMock != null) {
            btnMock.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    MockLocationService.setGpsMode(MainActivity.this, MockLocationService.MODE_MOCK_TETHER);
                    updateDialogUI.run();
                    Toast.makeText(MainActivity.this, "✓ GPS Compartido por Celular Activo (Puerto UDP 10110)", Toast.LENGTH_LONG).show();
                }
            });
        }

        if (btnReset != null) {
            btnReset.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    MockLocationService.restoreNativeHardwareGps(MainActivity.this);
                    updateDialogUI.run();
                    Toast.makeText(MainActivity.this, "✓ GPS satelital restablecido a modo nativo", Toast.LENGTH_SHORT).show();
                }
            });
        }

        dialog.show();
    }

    private String getWifiIpAddress() {
        try {
            WifiManager wm = (WifiManager) getApplicationContext().getSystemService(WIFI_SERVICE);
            if (wm != null && wm.getConnectionInfo() != null) {
                int ip = wm.getConnectionInfo().getIpAddress();
                if (ip != 0) {
                    return Formatter.formatIpAddress(ip);
                }
            }
        } catch (Exception ignored) {}
        return "192.168.43.1 (Hotspot Móvil)";
    }

    // ========================================================================
    // 12. DYNAMIC HARDWARE KEY RECEIVER (STEERING WHEEL & COAGENT)
    // ========================================================================
    private void registerHardwareKeyReceiver() {
        if (dynamicHardwareKeyReceiver != null) return;
        dynamicHardwareKeyReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                if (intent == null || intent.getAction() == null) return;
                String action = intent.getAction();

                if ("com.chinatsp.launcher_KEYHOME_SWIPE".equals(action)
                        || "com.chinatsp.action.ACTION_KEYHOME_SWIPE".equals(action)
                        || "com.chinatsp.action.HOME".equals(action)
                        || "com.chinatsp.launcher.home".equals(action)
                        || "com.chinatsp.systemui.ACTION_HOME".equals(action)) {
                    if (videoOverlayContainer != null && videoOverlayContainer.getVisibility() == View.VISIBLE) {
                        dismissIntroVideo();
                    }
                    setImmersiveMode();
                } else if ("com.coagent.intent.action.KEY_CHANGED".equals(action)) {
                    int kc = intent.getIntExtra("Key_code", intent.getIntExtra("keyCode", intent.getIntExtra("key_code", -1)));
                    String keyStr = intent.getStringExtra("Key_code");
                    if (keyStr == null) keyStr = intent.getStringExtra("key");
                    if (keyStr == null) keyStr = intent.getStringExtra("key_code");

                    if (kc == 27 || (keyStr != null && (keyStr.toLowerCase().contains("cam") || keyStr.toLowerCase().contains("avm")))) {
                        launchCamera();
                    } else if (kc == 3 || (keyStr != null && (keyStr.toLowerCase().contains("home") || "src".equalsIgnoreCase(keyStr)))) {
                        if (videoOverlayContainer != null && videoOverlayContainer.getVisibility() == View.VISIBLE) {
                            dismissIntroVideo();
                        }
                        setImmersiveMode();
                    }
                } else if (android.bluetooth.BluetoothDevice.ACTION_ACL_CONNECTED.equals(action)
                        || android.bluetooth.BluetoothDevice.ACTION_ACL_DISCONNECTED.equals(action)
                        || android.bluetooth.BluetoothAdapter.ACTION_STATE_CHANGED.equals(action)
                        || android.bluetooth.BluetoothAdapter.ACTION_CONNECTION_STATE_CHANGED.equals(action)) {
                    updateBluetoothStatusUI();
                } else if ("android.net.wifi.STATE_CHANGE".equals(action)) {
                    updateGpsStatusUI();
                }
            }
        };

        IntentFilter filter = new IntentFilter();
        filter.addAction("com.chinatsp.launcher_KEYHOME_SWIPE");
        filter.addAction("com.chinatsp.action.ACTION_KEYHOME_SWIPE");
        filter.addAction("com.chinatsp.action.HOME");
        filter.addAction("com.chinatsp.launcher.home");
        filter.addAction("com.chinatsp.systemui.ACTION_HOME");
        filter.addAction("com.coagent.intent.action.KEY_CHANGED");
        filter.addAction(android.bluetooth.BluetoothDevice.ACTION_ACL_CONNECTED);
        filter.addAction(android.bluetooth.BluetoothDevice.ACTION_ACL_DISCONNECTED);
        filter.addAction(android.bluetooth.BluetoothAdapter.ACTION_STATE_CHANGED);
        filter.addAction(android.bluetooth.BluetoothAdapter.ACTION_CONNECTION_STATE_CHANGED);
        filter.addAction("android.net.wifi.STATE_CHANGE");
        try {
            registerReceiver(dynamicHardwareKeyReceiver, filter);
        } catch (Exception ignored) {}
    }

    private void unregisterHardwareKeyReceiver() {
        if (dynamicHardwareKeyReceiver != null) {
            try {
                unregisterReceiver(dynamicHardwareKeyReceiver);
            } catch (Exception ignored) {}
            dynamicHardwareKeyReceiver = null;
        }
    }

    /**
     * BYPASS FORENSE F202_SystemUI:
     * Transmite los Broadcasts y propiedades exactas para eliminar las barras laterales (320px)
     * y liberar los 1920x720 pixeles nativos de la pantalla Changan X7 Plus.
     */
    private void unlockChanganF202Fullscreen() {
        try {
            // 1. Broadcast de Autorización Dinámica a PageChangeHandler$6 (appCentered = 2)
            Intent authIntent = new Intent("com.chinatsp.systemui.ACTION_APP_INFO");
            authIntent.putExtra("packageName", getPackageName());
            authIntent.putExtra("appCentered", 2);
            sendBroadcast(authIntent);

            // 2. Broadcast de Ocultación de Barra de Estado Propietaria
            Intent hideBarIntent = new Intent("com.android.intent.action.ACTION_HIDE_CUSTOM_STATUS_BAR");
            hideBarIntent.putExtra("packageName", getPackageName());
            sendBroadcast(hideBarIntent);

            // 3. Notificación de Actividad Reanudada para forzar hideNaviBar() y hideThirdAppFullScreen()
            Intent resumeIntent = new Intent("com.chinatsp.activity.onpostresume");
            resumeIntent.putExtra("packageName", getPackageName());
            sendBroadcast(resumeIntent);
            
            android.util.Log.i("ChanganCockpit", "[F202_BYPASS] Broadcasts de desbloqueo transmitidos exitosamente a F202_SystemUI");
        } catch (Exception e) {
            android.util.Log.e("ChanganCockpit", "[F202_BYPASS] Error transmitiendo broadcasts", e);
        }
    }

    // ========================================================================
    // PERSONALIZACIÓN, FONDOS DINÁMICOS & SWITCHER DE LAUNCHERS
    // ========================================================================
    private void applySavedWallpaper() {
        if (ivBg == null) return;
        try {
            String customPath = prefs.getString(KEY_WALLPAPER_PATH, null);
            if (customPath != null && !customPath.isEmpty()) {
                File f = new File(customPath);
                if (f.exists() && f.length() > 0) {
                    Bitmap bmp = BitmapFactory.decodeFile(customPath);
                    if (bmp != null) {
                        ivBg.setImageBitmap(bmp);
                        return;
                    }
                }
            }
            String wallpaperName = prefs.getString("custom_wallpaper_name", "bg_cockpit");
            int resId = getResources().getIdentifier(wallpaperName, "drawable", getPackageName());
            if (resId == 0) {
                resId = R.drawable.bg_cockpit;
            }
            ivBg.setImageResource(resId);
        } catch (Exception e) {
            ivBg.setImageResource(R.drawable.bg_cockpit);
        }
    }

    private void showPersonalizationDialog() {
        try {
            final Dialog dialog = new Dialog(this, android.R.style.Theme_Black_NoTitleBar_Fullscreen);
            dialog.setContentView(R.layout.dialog_personalizacion);
            if (dialog.getWindow() != null) {
                dialog.getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
                dialog.getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN);
            }

            // Cerrar
            View btnClose = dialog.findViewById(R.id.btn_close_personalizacion);
            if (btnClose != null) {
                btnClose.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        dialog.dismiss();
                        setImmersiveMode();
                    }
                });
            }

            // Temas de Fondo Panorámico
            View cardSuv = dialog.findViewById(R.id.card_theme_suv);
            if (cardSuv != null) {
                cardSuv.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        prefs.edit().putString("custom_wallpaper_name", "bg_cockpit")
                                    .remove(KEY_WALLPAPER_RES)
                                    .remove(KEY_WALLPAPER_PATH).apply();
                        applySavedWallpaper();
                        Toast.makeText(MainActivity.this, "✓ Tema Oshan X7 Luxury SUV Aplicado", Toast.LENGTH_SHORT).show();
                        dialog.dismiss();
                        setImmersiveMode();
                    }
                });
            }

            View cardNeon = dialog.findViewById(R.id.card_theme_neon);
            if (cardNeon != null) {
                cardNeon.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        prefs.edit().putString("custom_wallpaper_name", "bg_wallpaper_neon")
                                    .remove(KEY_WALLPAPER_RES)
                                    .remove(KEY_WALLPAPER_PATH).apply();
                        applySavedWallpaper();
                        Toast.makeText(MainActivity.this, "✓ Tema Cyber Neon HUD Aplicado", Toast.LENGTH_SHORT).show();
                        dialog.dismiss();
                        setImmersiveMode();
                    }
                });
            }

            View cardMinimal = dialog.findViewById(R.id.card_theme_minimal);
            if (cardMinimal != null) {
                cardMinimal.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        prefs.edit().putString("custom_wallpaper_name", "bg_wallpaper_minimal")
                                    .remove(KEY_WALLPAPER_RES)
                                    .remove(KEY_WALLPAPER_PATH).apply();
                        applySavedWallpaper();
                        Toast.makeText(MainActivity.this, "✓ Tema Midnight Obsidian Aplicado", Toast.LENGTH_SHORT).show();
                        dialog.dismiss();
                        setImmersiveMode();
                    }
                });
            }

            View cardSunset = dialog.findViewById(R.id.card_theme_sunset);
            if (cardSunset != null) {
                cardSunset.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        prefs.edit().putString("custom_wallpaper_name", "bg_wallpaper_sunset")
                                    .remove(KEY_WALLPAPER_RES)
                                    .remove(KEY_WALLPAPER_PATH).apply();
                        applySavedWallpaper();
                        Toast.makeText(MainActivity.this, "✓ Tema Sunset Horizon GT Aplicado", Toast.LENGTH_SHORT).show();
                        dialog.dismiss();
                        setImmersiveMode();
                    }
                });
            }

            // Cargar imagen personalizada
            Button btnPick = dialog.findViewById(R.id.btn_pick_custom_wallpaper);
            if (btnPick != null) {
                btnPick.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        try {
                            Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
                            intent.setType("image/*");
                            intent.addCategory(Intent.CATEGORY_OPENABLE);
                            startActivityForResult(Intent.createChooser(intent, "Seleccionar Fondo"), REQ_PICK_WALLPAPER);
                            dialog.dismiss();
                        } catch (Exception ex) {
                            Toast.makeText(MainActivity.this, "Coloca imágenes en /sdcard/Changan/Wallpapers/", Toast.LENGTH_LONG).show();
                        }
                    }
                });
            }

            // Explorar carpeta /sdcard/Changan/Wallpapers/
            Button btnScan = dialog.findViewById(R.id.btn_scan_wallpapers_folder);
            if (btnScan != null) {
                btnScan.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        cycleCustomWallpapersFromFolder();
                        dialog.dismiss();
                    }
                });
            }

            // Controles de Video
            final Button btnAlways = dialog.findViewById(R.id.btn_toggle_video_always);
            final Button btnCooldown = dialog.findViewById(R.id.btn_toggle_video_cooldown);
            final Button btnRandom = dialog.findViewById(R.id.btn_toggle_video_random);
            Button btnTest = dialog.findViewById(R.id.btn_test_play_video);

            int currentMode = prefs.getInt(KEY_VIDEO_MODE, 0);
            updateVideoModeButtons(btnAlways, btnCooldown, currentMode);

            if (btnAlways != null) {
                btnAlways.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        prefs.edit().putInt(KEY_VIDEO_MODE, 0).apply();
                        updateVideoModeButtons(btnAlways, btnCooldown, 0);
                        Toast.makeText(MainActivity.this, "✓ Video: Siempre en cada inicio (Reemplaza Hello)", Toast.LENGTH_SHORT).show();
                    }
                });
            }

            if (btnCooldown != null) {
                btnCooldown.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        prefs.edit().putInt(KEY_VIDEO_MODE, 1).apply();
                        updateVideoModeButtons(btnAlways, btnCooldown, 1);
                        Toast.makeText(MainActivity.this, "✓ Video: Solo inicio en frío (30 min)", Toast.LENGTH_SHORT).show();
                    }
                });
            }

            boolean isRand = prefs.getBoolean(KEY_VIDEO_RANDOM, true);
            if (btnRandom != null) {
                btnRandom.setText(isRand ? "🎲 Modo Aleatorio: ACTIVADO" : "🎲 Modo Aleatorio: DESACTIVADO");
                btnRandom.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        boolean newVal = !prefs.getBoolean(KEY_VIDEO_RANDOM, true);
                        prefs.edit().putBoolean(KEY_VIDEO_RANDOM, newVal).apply();
                        btnRandom.setText(newVal ? "🎲 Modo Aleatorio: ACTIVADO" : "🎲 Modo Aleatorio: DESACTIVADO");
                        Toast.makeText(MainActivity.this, newVal ? "Modo aleatorio activado" : "Modo aleatorio desactivado", Toast.LENGTH_SHORT).show();
                    }
                });
            }

            if (btnTest != null) {
                btnTest.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        dialog.dismiss();
                        playIntroVideo(true);
                    }
                });
            }

            // Launcher OnStyle original
            Button btnOnStyle = dialog.findViewById(R.id.btn_switch_to_onstyle);
            if (btnOnStyle != null) {
                btnOnStyle.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        dialog.dismiss();
                        switchToOnStyleLauncher();
                    }
                });
            }

            // YGPS Monitor
            Button btnYgps = dialog.findViewById(R.id.btn_open_ygps_monitor);
            if (btnYgps != null) {
                btnYgps.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        dialog.dismiss();
                        openYgps();
                    }
                });
            }

            // Ajustes del Vehículo
            Button btnSettings = dialog.findViewById(R.id.btn_open_car_settings);
            if (btnSettings != null) {
                btnSettings.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        dialog.dismiss();
                        launchSettings();
                    }
                });
            }

            // Ajustes del Teléfono / Android
            Button btnPhoneSettings = dialog.findViewById(R.id.btn_open_phone_settings);
            if (btnPhoneSettings != null) {
                btnPhoneSettings.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        dialog.dismiss();
                        launchPhoneSettings();
                    }
                });
            }

            // Burbuja Flotante de Retroceso
            Button btnFloatingBubble = dialog.findViewById(R.id.btn_toggle_floating_bubble);
            if (btnFloatingBubble != null) {
                btnFloatingBubble.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        restartFloatingBubble();
                    }
                });
            }

            dialog.show();
        } catch (Exception e) {
            Toast.makeText(this, "Ajustes de personalización abiertos", Toast.LENGTH_SHORT).show();
        }
    }

    private void updateVideoModeButtons(Button btnAlways, Button btnCooldown, int mode) {
        if (btnAlways != null) {
            if (mode == 0) {
                btnAlways.setBackgroundResource(R.drawable.bg_side_home_active);
                btnAlways.setTextColor(Color.WHITE);
            } else {
                btnAlways.setBackgroundResource(R.drawable.bg_sidebar_btn);
                btnAlways.setTextColor(Color.parseColor("#94A3B8"));
            }
        }
        if (btnCooldown != null) {
            if (mode == 1) {
                btnCooldown.setBackgroundResource(R.drawable.bg_side_home_active);
                btnCooldown.setTextColor(Color.WHITE);
            } else {
                btnCooldown.setBackgroundResource(R.drawable.bg_sidebar_btn);
                btnCooldown.setTextColor(Color.parseColor("#94A3B8"));
            }
        }
    }

    private void cycleCustomWallpapersFromFolder() {
        try {
            File dir = new File(Environment.getExternalStorageDirectory(), "Changan/Wallpapers");
            if (!dir.exists()) {
                dir.mkdirs();
            }
            File[] files = dir.listFiles(new FileFilter() {
                @Override
                public boolean accept(File file) {
                    if (file.isFile()) {
                        String n = file.getName().toLowerCase();
                        return n.endsWith(".jpg") || n.endsWith(".png") || n.endsWith(".jpeg") || n.endsWith(".webp");
                    }
                    return false;
                }
            });
            if (files == null || files.length == 0) {
                Toast.makeText(this, "No hay imágenes en /sdcard/Changan/Wallpapers/\nPuedes copiar imágenes 1920x720 por USB.", Toast.LENGTH_LONG).show();
                return;
            }
            String current = prefs.getString(KEY_WALLPAPER_PATH, "");
            int nextIndex = 0;
            for (int i = 0; i < files.length; i++) {
                if (files[i].getAbsolutePath().equals(current)) {
                    nextIndex = (i + 1) % files.length;
                    break;
                }
            }
            String chosen = files[nextIndex].getAbsolutePath();
            prefs.edit().putString(KEY_WALLPAPER_PATH, chosen).apply();
            applySavedWallpaper();
            Toast.makeText(this, "✓ Fondo aplicado: " + files[nextIndex].getName(), Toast.LENGTH_SHORT).show();
        } catch (Exception ex) {
            Toast.makeText(this, "Error al leer /sdcard/Changan/Wallpapers/", Toast.LENGTH_SHORT).show();
        }
    }

    private void launchPhoneSettings() {
        try {
            Intent intent = new Intent(android.provider.Settings.ACTION_SETTINGS);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        } catch (Exception e) {
            try {
                Intent intent = new Intent();
                intent.setComponent(new ComponentName("com.android.settings", "com.android.settings.Settings"));
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(intent);
            } catch (Exception ex) {
                Toast.makeText(this, "Ajustes del teléfono no encontrados", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void restartFloatingBubble() {
        try {
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.M) {
                if (!android.provider.Settings.canDrawOverlays(this)) {
                    Intent intent = new Intent(android.provider.Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                            Uri.parse("package:" + getPackageName()));
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    startActivity(intent);
                    Toast.makeText(this, "Por favor concede permiso de superposición", Toast.LENGTH_LONG).show();
                    return;
                }
            }
            startService(new Intent(this, FloatingOverlayService.class));
            Toast.makeText(this, "✓ Burbuja flotante de retroceso visible en pantalla", Toast.LENGTH_SHORT).show();
        } catch (Exception e) {
            Toast.makeText(this, "Error activando burbuja flotante", Toast.LENGTH_SHORT).show();
        }
    }

    private void switchToOnStyleLauncher() {
        try {
            Intent intent = new Intent();
            intent.setComponent(new ComponentName("com.chinatsp.launcher", "com.chinatsp.launcher.MainAct"));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        } catch (Exception e) {
            try {
                Intent intent = getPackageManager().getLaunchIntentForPackage("com.chinatsp.launcher");
                if (intent != null) {
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    startActivity(intent);
                    return;
                }
            } catch (Exception ignored) {}
            Toast.makeText(this, "Launcher OnStyle no encontrado", Toast.LENGTH_SHORT).show();
        }
    }

    private void openYgps() {
        try {
            Intent intent = new Intent();
            intent.setComponent(new ComponentName("com.mediatek.ygps", "com.mediatek.ygps.YgpsActivity"));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        } catch (Exception e) {
            try {
                Intent sIntent = new Intent(android.provider.Settings.ACTION_LOCATION_SOURCE_SETTINGS);
                sIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(sIntent);
            } catch (Exception ex) {
                Toast.makeText(this, "YGPS no disponible", Toast.LENGTH_SHORT).show();
            }
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQ_PICK_WALLPAPER && resultCode == RESULT_OK && data != null && data.getData() != null) {
            try {
                Uri imageUri = data.getData();
                File dir = new File(Environment.getExternalStorageDirectory(), "Changan/Wallpapers");
                if (!dir.exists()) dir.mkdirs();
                File dest = new File(dir, "custom_wallpaper_" + System.currentTimeMillis() + ".jpg");

                InputStream in = getContentResolver().openInputStream(imageUri);
                FileOutputStream out = new FileOutputStream(dest);
                byte[] buf = new byte[8192];
                int len;
                while ((len = in.read(buf)) > 0) {
                    out.write(buf, 0, len);
                }
                in.close();
                out.close();

                prefs.edit().putString(KEY_WALLPAPER_PATH, dest.getAbsolutePath()).apply();
                applySavedWallpaper();
                Toast.makeText(this, "✓ Fondo personalizado guardado y aplicado", Toast.LENGTH_SHORT).show();
            } catch (Exception e) {
                Toast.makeText(this, "Error al importar fondo seleccionado", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void clearLauncherCacheAndRefresh() {
        try {
            File cacheDir = getCacheDir();
            if (cacheDir != null && cacheDir.isDirectory()) {
                File[] files = cacheDir.listFiles();
                if (files != null) {
                    for (File f : files) {
                        try { f.delete(); } catch (Exception ignored) {}
                    }
                }
            }
            File extCache = getExternalCacheDir();
            if (extCache != null && extCache.isDirectory()) {
                File[] files = extCache.listFiles();
                if (files != null) {
                    for (File f : files) {
                        try { f.delete(); } catch (Exception ignored) {}
                    }
                }
            }
        } catch (Exception ignored) {}

        setupSecondHomeGrid();
        setupBottomFavoritesDock();
        Toast.makeText(this, "⟳ Caché e iconos actualizados", Toast.LENGTH_SHORT).show();
    }

    private void openWebInBrave(String url) {
        applyFullscreenBypass("com.brave.browser");
        try {
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
            intent.setPackage("com.brave.browser");
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        } catch (Exception e) {
            try {
                Intent generic = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                generic.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(generic);
            } catch (Exception ignored) {}
        }
    }

}

