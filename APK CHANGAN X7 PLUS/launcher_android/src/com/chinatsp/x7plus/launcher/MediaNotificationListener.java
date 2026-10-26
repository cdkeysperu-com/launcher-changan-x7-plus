package com.chinatsp.x7plus.launcher;

import android.app.Notification;
import android.graphics.Bitmap;
import android.graphics.drawable.Icon;
import android.os.Bundle;
import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;
import java.lang.ref.WeakReference;

public class MediaNotificationListener extends NotificationListenerService {

    public interface MediaListener {
        void onMediaUpdated(String title, String artist, Bitmap albumArt, boolean isPlaying);
    }

    private static WeakReference<MediaListener> currentListenerRef = null;

    public static void setMediaListener(MediaListener listener) {
        if (listener == null) {
            currentListenerRef = null;
        } else {
            currentListenerRef = new WeakReference<>(listener);
        }
    }

    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {
        if (sbn == null || sbn.getNotification() == null) return;

        String pkg = sbn.getPackageName();
        if (pkg != null) {
            String lowerPkg = pkg.toLowerCase();
            // Strict blacklist for navigation, system, downloads, tethers, background services
            if (lowerPkg.contains("waze") || lowerPkg.contains("map") || lowerPkg.contains("nav")
                    || lowerPkg.contains("gps") || lowerPkg.contains("systemui") || lowerPkg.contains("android.providers")
                    || lowerPkg.contains("download") || lowerPkg.contains("settings") || lowerPkg.contains("tether")
                    || lowerPkg.contains("androidauto") || lowerPkg.contains("gearhead") || lowerPkg.contains("carlink")
                    || lowerPkg.contains("headunit") || lowerPkg.contains("bricatta") || lowerPkg.contains("snoopy112")
                    || lowerPkg.contains("overlay") || lowerPkg.contains("service")) {
                return;
            }
        }

        Notification notif = sbn.getNotification();
        Bundle extras = notif.extras;
        if (extras == null) return;

        CharSequence title = extras.getCharSequence(Notification.EXTRA_TITLE);
        CharSequence artist = extras.getCharSequence(Notification.EXTRA_TEXT);
        if (artist == null) {
            artist = extras.getCharSequence(Notification.EXTRA_SUB_TEXT);
        }

        if (title != null && title.length() > 0) {
            String titleStr = title.toString();
            String artistStr = (artist != null) ? artist.toString() : "";
            String lowerTitle = titleStr.toLowerCase();
            String lowerArtist = artistStr.toLowerCase();

            // Filtrar textos de navegacion, servicios en primer plano y alertas de sistema
            if (lowerTitle.contains("waze") || lowerTitle.contains("maps") || lowerTitle.contains("en marcha")
                    || lowerTitle.contains("segundo plano") || lowerTitle.contains("background")
                    || lowerTitle.contains("naveg") || lowerTitle.contains("ruta")
                    || lowerTitle.contains("alerta") || lowerTitle.contains("conectad")
                    || lowerTitle.contains("bater") || lowerTitle.contains("descarg")
                    || lowerTitle.contains("toca para") || lowerTitle.contains("ejecut")
                    || lowerTitle.contains("headunit") || lowerTitle.contains("open headunit")
                    || lowerArtist.contains("segundo plano") || lowerArtist.contains("background")
                    || lowerArtist.contains("toca para abrir") || lowerArtist.contains("ejecut")
                    || lowerArtist.contains("headunit")) {
                return;
            }

            Bitmap art = null;
            Object largeIconObj = extras.get(Notification.EXTRA_LARGE_ICON);
            if (largeIconObj instanceof Bitmap) {
                art = (Bitmap) largeIconObj;
            }

            if (currentListenerRef != null) {
                MediaListener listener = currentListenerRef.get();
                if (listener != null) {
                    listener.onMediaUpdated(titleStr, artistStr, art, true);
                }
            }
        }
    }

    @Override
    public void onNotificationRemoved(StatusBarNotification sbn) {}
}
