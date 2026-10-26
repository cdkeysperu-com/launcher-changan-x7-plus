# -*- coding: utf-8 -*-
"""
Script de actualización integral de MainActivity.java para Changan X7 Plus
Implementa:
1. Cámara 360 HD (BuiltinHDCameraActivity - Foto 3) eliminando avmlive (Foto 2).
2. Música directa Changan (com.chinatsp.music) sin cuadros de diálogo.
3. Segundo Home (Page 2) con deslizamiento horizontal (ViewFlipper + GestureDetector).
4. Cero iconos en blanco (loadRobustAppIcon con badges automotrices de alta tecnología).
5. Barra de Favoritos personalizable con iconos dinámicos y pulsación larga.
6. Bypass de bordes negros fullscreen (appCentered 2) en todos los lanzamientos.
7. Activación de FloatingBackService en segundo plano.
"""
import os
import re

target = r'APK CHANGAN X7 PLUS/launcher_android/src/com/chinatsp/x7plus/launcher/MainActivity.java'
with open(target, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Imports
imports = """
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.Typeface;
import android.graphics.drawable.BitmapDrawable;
import android.view.GestureDetector;
import android.widget.ViewFlipper;
"""
if "import android.graphics.Canvas;" not in code:
    code = code.replace("import android.graphics.Bitmap;", "import android.graphics.Bitmap;\n" + imports)

# 2. Member variables
members = """
    // ViewFlipper & Second Home Elements
    private ViewFlipper viewFlipper;
    private View dotPage1;
    private View dotPage2;
    private GestureDetector gestureDetector;
    private GridView gvSecondHome;
"""
if "private ViewFlipper viewFlipper;" not in code:
    code = code.replace("private SharedPreferences prefs;", "private SharedPreferences prefs;\n" + members)

# 3. In onCreate():
# add setupPageGestures() and start FloatingBackService
old_oncreate_tail = """        // 5. Start GPS Mock Provider Service
        try {
            startService(new Intent(this, MockLocationService.class));
        } catch (Exception ignored) {}

        // 6. Handle Intro Video on Cold Start with 5-Hour Smart Cooldown
        setupStartupVideo();"""

new_oncreate_tail = """        // 5. Setup ViewFlipper Gestures & Second Home
        setupPageGestures();

        // 6. Start Native Floating Back & Home Service
        try {
            startService(new Intent(this, FloatingBackService.class));
        } catch (Exception ignored) {}

        // 7. Start GPS Real-Time Hardware Telemetry Service
        try {
            startService(new Intent(this, MockLocationService.class));
        } catch (Exception ignored) {}

        // 8. Handle Intro Video on Cold Start with 5-Hour Smart Cooldown
        setupStartupVideo();"""

code = code.replace(old_oncreate_tail, new_oncreate_tail)

# 4. In dispatchTouchEvent:
dispatch_touch = """
    @Override
    public boolean dispatchTouchEvent(MotionEvent ev) {
        if (gestureDetector != null) {
            gestureDetector.onTouchEvent(ev);
        }
        return super.dispatchTouchEvent(ev);
    }
"""
if "public boolean dispatchTouchEvent(MotionEvent ev)" not in code:
    code = code.replace("private void initViews() {", dispatch_touch + "\n    private void initViews() {")

# 5. In setupSidebarButtons():
# btn_side_home -> showPage(0), btn_side_apps -> showPage(1)
old_side_home = """        findViewById(R.id.btn_side_home).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                setImmersiveMode();
            }
        });"""

new_side_home = """        findViewById(R.id.btn_side_home).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showPage(0);
                setImmersiveMode();
            }
        });"""

code = code.replace(old_side_home, new_side_home)

old_side_apps = """        findViewById(R.id.btn_side_apps).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showAppDrawer();
            }
        });"""

new_side_apps = """        findViewById(R.id.btn_side_apps).setOnClickListener(new View.OnClickListener() {
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
        });"""

code = code.replace(old_side_apps, new_side_apps)

# 6. Replace launchCamera() with real BuiltinHDCameraActivity
old_launch_camera = """    private void launchCamera() {
        // ============================================================
        // CÁMARA 360° PANORÁMICA DE GUÍA (Estacionamiento, Reversa, 2D/3D, Proximidad)
        // NUNCA abrir com.chinatsp.dvrcamera.builtin.BuiltinDVRActivity (grabadora DVR de viaje)
        // ============================================================
        triggerAvm360Broadcasts();

        // 1. Enviar eventos y broadcasts nativos Changan para AVM 360
        triggerAvm360Broadcasts();

        // 2. Actividades nativas de asistencia de aparcamiento / AVM (APA / Surround 360)
        String[][] avmTargets = {
            {"com.chinatsp.dvrcamera", "com.chinatsp.dvrcamera.ApaActivity"},
            {"com.incall.avm", "com.incall.avm.AVMActivity"},
            {"com.chinatsp.avmlive", "com.chinatsp.avmlive.MainActivity"}
        };
        for (String[] target : avmTargets) {
            try {
                Intent apa = new Intent();
                apa.setComponent(new ComponentName(target[0], target[1]));
                apa.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED);
                startActivity(apa);
                return;
            } catch (Exception ignored) {}
        }

        Toast.makeText(this, "Cámara 360° Guía / Aparcamiento activada", Toast.LENGTH_SHORT).show();
    }"""

new_launch_camera = """    private void launchCamera() {
        // ============================================================
        // CÁMARA 360° PANORÁMICA REAL HD CHANGAN (Foto 3 - BuiltinHDCameraActivity)
        // NUNCA usar com.chinatsp.avmlive (Foto 2 - App Qianliyan con código QR)
        // ============================================================
        triggerAvm360Broadcasts();

        // 1. Actividad oficial Changan F202 AVM 360 Panorámica con menú de ángulos visuales
        try {
            Intent hdCamera = new Intent();
            hdCamera.setComponent(new ComponentName(
                "com.chinatsp.dvrcamera",
                "com.chinatsp.dvrcamera.builtin.hdcamera.BuiltinHDCameraActivity"
            ));
            hdCamera.setAction("android.chinatsp.intent.action.customize_camera");
            hdCamera.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED);
            startActivity(hdCamera);
            return;
        } catch (Exception ignored) {}

        // Fallbacks autorizados de cámara panorámica
        String[][] avmTargets = {
            {"com.chinatsp.dvrcamera", "com.chinatsp.dvrcamera.builtin.hdcamera.BuiltinHDCameraActivity"},
            {"com.chinatsp.dvrcamera", "com.chinatsp.dvrcamera.ApaActivity"},
            {"com.incall.avm", "com.incall.avm.AVMActivity"}
        };
        for (String[] target : avmTargets) {
            try {
                Intent apa = new Intent();
                apa.setComponent(new ComponentName(target[0], target[1]));
                apa.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED);
                startActivity(apa);
                return;
            } catch (Exception ignored) {}
        }

        Toast.makeText(this, "Cámara 360° Panorámica HD Changan", Toast.LENGTH_SHORT).show();
    }"""

code = code.replace(old_launch_camera, new_launch_camera)

# 7. Replace launchMusicPreferredOrSelector() to launch directly
old_launch_music = """    private void launchMusicPreferredOrSelector() {
        String defaultPkg = prefs.getString(KEY_DEFAULT_MUSIC, null);
        if (defaultPkg != null && !defaultPkg.isEmpty()) {
            Intent intent = getPackageManager().getLaunchIntentForPackage(defaultPkg);
            if (intent != null) {
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(intent);
                return;
            }
        }
        showMusicSelectorDialog();
    }"""

new_launch_music = """    private void launchMusicPreferredOrSelector() {
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
    }"""

code = code.replace(old_launch_music, new_launch_music)

# 8. Fullscreen bypass in launchAppOrToast and launchExplicit
old_launch_app = """    private void launchAppOrToast(String packageName, String name) {
        Intent intent = getPackageManager().getLaunchIntentForPackage(packageName);
        if (intent != null) {
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        } else {
            Toast.makeText(this, "Iniciando: " + name, Toast.LENGTH_SHORT).show();
        }
    }"""

new_launch_app = """    private void applyFullscreenBypass(String packageName) {
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
    }"""

code = code.replace(old_launch_app, new_launch_app)

# 9. Update launchNavigation prioritizing Waze and Magic Earth
old_launch_nav = """    private void launchNavigation() {
        String[] navPackages = {
            "com.generalmagic.magicearth",
            "app.organicmaps.web",
            "app.organicmaps",
            "com.waze",
            "gb.xxy.hr",
            "com.google.android.apps.maps"
        };
        for (String pkg : navPackages) {
            Intent intent = getPackageManager().getLaunchIntentForPackage(pkg);
            if (intent != null) {
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(intent);
                return;
            }
        }"""

new_launch_nav = """    private void launchNavigation() {
        String[] navPackages = {
            "com.waze",
            "com.generalmagic.magicearth",
            "app.organicmaps.web",
            "app.organicmaps",
            "com.google.android.apps.maps",
            "com.andrerinas.headunitrevived",
            "gb.xxy.hr"
        };
        for (String pkg : navPackages) {
            Intent intent = getPackageManager().getLaunchIntentForPackage(pkg);
            if (intent != null) {
                applyFullscreenBypass(pkg);
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(intent);
                return;
            }
        }"""

code = code.replace(old_launch_nav, new_launch_nav)

# 10. Update setupBottomFavoritesDock() to be customizable with dynamic icons and long-press
old_fav_dock = """    private void setupBottomFavoritesDock() {
        // Pill 1: Radio
        findViewById(R.id.btn_fav_radio).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchRadio();
            }
        });

        // Pill 2: Reproductor de música
        findViewById(R.id.btn_fav_music).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchMusicPreferredOrSelector();
            }
        });

        // Pill 3: Teléfono Bluetooth
        findViewById(R.id.btn_fav_phone).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchPhone();
            }
        });

        // Pill 4: Brave
        findViewById(R.id.btn_fav_brave).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchAppOrToast("com.brave.browser", "Brave Browser");
            }
        });

        // Pill 5: Apps (Cajón de Aplicaciones directo)
        View btnFavApps = findViewById(R.id.btn_fav_apps);
        if (btnFavApps != null) {
            btnFavApps.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    showAppDrawer();
                }
            });
        }

        // Pill 6: Control Rápido & Modos de Manejo Changan
        findViewById(R.id.btn_fav_add).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showQuickControlDialog();
            }
        });
    }"""

new_fav_dock = """    private void setupBottomFavoritesDock() {
        loadFavoritePill(0, R.id.btn_fav_radio, R.id.iv_fav_radio, R.id.tv_fav_radio, "com.chinatsp.radio", "Radio", R.drawable.ic_fav_radio);
        loadFavoritePill(1, R.id.btn_fav_music, R.id.iv_fav_music, R.id.tv_fav_music, "com.chinatsp.music", "Música Changan", R.drawable.ic_fav_music);
        loadFavoritePill(2, R.id.btn_fav_phone, R.id.iv_fav_phone, R.id.tv_fav_phone, "com.chinatsp.phone", "Teléfono Bluetooth", R.drawable.ic_fav_phone);
        loadFavoritePill(3, R.id.btn_fav_brave, R.id.iv_fav_brave, R.id.tv_fav_brave, "com.brave.browser", "Brave", R.drawable.icon_brave);
        loadFavoritePill(4, R.id.btn_fav_add, R.id.iv_fav_add, R.id.tv_fav_add, "com.waze", "Waze GPS", R.drawable.icon_waze);
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
    }"""

code = code.replace(old_fav_dock, new_fav_dock)

# 11. Add Page gestures, second home grid setup, and robust icon loading methods
new_methods = """
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
            String[] words = label.trim().split("\\\\s+");
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
"""

if "setupSecondHomeGrid()" not in code:
    code = code.replace("    // ========================================================================\n    // 10. APPLICATION DRAWER", new_methods + "\n    // ========================================================================\n    // 10. APPLICATION DRAWER")

# 12. Update showAppDrawer() to also use loadRobustAppIcon and applyFullscreenBypass
old_drawer_getview = """                    if (iv != null) {
                        String pkg = info.activityInfo.packageName;
                        android.graphics.drawable.Drawable icon = null;
                        if ("com.waze".equals(pkg)) {
                            try {
                                icon = getResources().getDrawable(R.drawable.icon_waze);
                            } catch (Exception ignored) {}
                        } else if ("com.brave.browser".equals(pkg)) {
                            try {
                                icon = getResources().getDrawable(R.drawable.icon_brave);
                            } catch (Exception ignored) {}
                        } else if ("com.chinatsp.x7plus.launcher".equals(pkg)) {
                            try {
                                icon = getResources().getDrawable(R.drawable.ic_launcher);
                            } catch (Exception ignored) {}
                        }
                        if (icon == null) {
                            try {
                                icon = info.loadIcon(pm);
                            } catch (Exception ignored) {}
                        }
                        if (icon == null) {
                            try {
                                icon = getResources().getDrawable(R.drawable.ic_apps);
                            } catch (Exception ignored) {}
                        }
                        iv.setImageDrawable(icon);
                    }"""

new_drawer_getview = """                    if (iv != null) {
                        iv.setImageDrawable(loadRobustAppIcon(info, pm));
                    }"""

code = code.replace(old_drawer_getview, new_drawer_getview)

old_drawer_click = """                    ResolveInfo info = appList.get(position);
                    Intent launchIntent = pm.getLaunchIntentForPackage(info.activityInfo.packageName);
                    if (launchIntent != null) {
                        launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                        dialog.dismiss();
                        startActivity(launchIntent);
                    }"""

new_drawer_click = """                    ResolveInfo info = appList.get(position);
                    String selPkg = info.activityInfo.packageName;
                    applyFullscreenBypass(selPkg);
                    Intent launchIntent = pm.getLaunchIntentForPackage(selPkg);
                    if (launchIntent != null) {
                        launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                        dialog.dismiss();
                        startActivity(launchIntent);
                    }"""

code = code.replace(old_drawer_click, new_drawer_click)

with open(target, 'w', encoding='utf-8') as f:
    f.write(code)

print("MainActivity.java patched successfully!")
