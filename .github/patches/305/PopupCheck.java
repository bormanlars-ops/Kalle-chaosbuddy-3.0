package de.boyka.kallebuddy;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Context;
import android.content.Intent;
import android.graphics.PixelFormat;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.TextView;

/** Real permission diagnostics and a user-triggered 10-second overlay preview. */
final class PopupCheck {
    private PopupCheck(){}

    static boolean ready(Context c){
        NotificationManager nm=c.getSystemService(NotificationManager.class);
        NotificationChannel ch=nm.getNotificationChannel(AlarmService.CHANNEL);
        return nm.areNotificationsEnabled()
            && ch!=null && ch.getImportance()>=NotificationManager.IMPORTANCE_HIGH
            && Scheduler.allowed(c)
            && Settings.canDrawOverlays(c)
            && Store.prefs(c).getBoolean("reminders",true)
            && Store.prefs(c).getBoolean("missionPopups",true);
    }
    static String state(Context c){
        NotificationManager nm=c.getSystemService(NotificationManager.class);
        NotificationChannel ch=nm.getNotificationChannel(AlarmService.CHANNEL);
        return "Benachrichtigungen: "+(nm.areNotificationsEnabled()?"ERLAUBT":"FEHLEN")+"\n"
            +"Missionskanal: "+(ch!=null&&ch.getImportance()>=NotificationManager.IMPORTANCE_HIGH?"POP-UP-FÄHIG":"PRÜFEN")+"\n"
            +"Über anderen Apps anzeigen: "+(Settings.canDrawOverlays(c)?"ERLAUBT":"FEHLT")+"\n"
            +"Genaue Alarme: "+(Scheduler.allowed(c)?"ERLAUBT":"FEHLEN")+"\n"
            +"Missionsfenster aktiviert: "+(Store.prefs(c).getBoolean("missionPopups",true)?"JA":"NEIN")+"\n"
            +"Missionserinnerungen aktiviert: "+(Store.prefs(c).getBoolean("reminders",true)?"JA":"NEIN");
    }
    static void guide(MainActivity a){
        a.getSystemService(NotificationManager.class).createNotificationChannel(AlarmService.channel());
        new AlertDialog.Builder(a)
            .setTitle("KALLE / POP-UPS AKTIVIEREN")
            .setMessage("Diese Test-App ist eine EIGENE Android-App. Die Freigaben und Missionen der alten Kalle-Version werden nicht übernommen.\n\n"
                +state(a)
                +"\n\nBitte in den Kalle-Einstellungen Benachrichtigungen, Pop-up-Kanal, genaue Alarme und 'Über anderen Apps' erlauben. Danach die zwei Testknöpfe benutzen.")
            .setPositiveButton("EINSTELLUNGEN", (d,w)->a.settings())
            .setNegativeButton("SPÄTER",null).show();
    }
    static void overlayPreview(Activity a){
        if(!Settings.canDrawOverlays(a)){
            new AlertDialog.Builder(a).setTitle("Missionsfenster blockiert")
                .setMessage("Android erlaubt dieser Test-App das Einblenden über anderen Apps noch nicht. Aktiviere 'Über anderen Apps anzeigen'.")
                .setPositiveButton("FREIGABE ÖFFNEN",(d,w)->a.startActivity(
                    new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                        android.net.Uri.parse("package:"+a.getPackageName()))))
                .setNegativeButton("ZURÜCK",null).show();
            return;
        }
        final WindowManager manager=a.getSystemService(WindowManager.class);
        final TextView view=new TextView(a);
        view.setText("KALLE / POP-UP-TEST\n\nICH BIN DA, DIGGA! 😤\nDies ist ein echtes schwebendes Testfenster.\nZum Schließen antippen.");
        view.setTextColor(0xffffebc0);
        view.setTextSize(19f);
        view.setPadding(Ui.dp(a,18),Ui.dp(a,15),Ui.dp(a,18),Ui.dp(a,15));
        view.setBackground(Ui.shape(0xff392421,Ui.dp(a,15)));
        int width=Math.min(a.getResources().getDisplayMetrics().widthPixels-Ui.dp(a,20),Ui.dp(a,460));
        WindowManager.LayoutParams p=new WindowManager.LayoutParams(
            width,WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE|WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
            PixelFormat.TRANSLUCENT);
        p.gravity=Gravity.TOP|Gravity.CENTER_HORIZONTAL;
        p.y=Ui.dp(a,75);
        p.setTitle("Kalle Pop-up-Selbsttest");
        final Handler handler=new Handler(Looper.getMainLooper());
        final Runnable close=()->{try{if(view.getParent()!=null)manager.removeView(view);}catch(RuntimeException ignored){}};
        view.setOnClickListener(v->{handler.removeCallbacks(close);close.run();});
        try{
            manager.addView(view,p);
            handler.postDelayed(close,10000);
        }catch(RuntimeException error){
            new AlertDialog.Builder(a).setTitle("Pop-up-Test fehlgeschlagen")
                .setMessage("Android hat das schwebende Fenster blockiert: "+error.getClass().getSimpleName()
                    +"\nPrüfe die Freigabe 'Über anderen Apps anzeigen'.")
                .setPositiveButton("OK",null).show();
        }
    }
}
