#!/usr/bin/env python3
"""Apply 3.0.5 pop-up repair after .github/patches/304/apply304.py.
Never reads, signs with, or exposes the private signing backup.
"""
from pathlib import Path

project=Path.cwd()
root=project/"app/src/main/java/de/boyka/kallebuddy"
main=root/"MainActivity.java"
alarm=root/"AlarmService.java"
store=root/"Store.java"
manifest=project/"app/src/main/AndroidManifest.xml"
gradle=project/"app/build.gradle"

def replace(path,old,new,expected=1):
    s=path.read_text(encoding="utf-8")
    count=s.count(old)
    if count!=expected:
        raise RuntimeError(f"{path}: wanted {expected} x {old[:75]!r}, got {count}")
    path.write_text(s.replace(old,new,expected),encoding="utf-8")

# First launch: explain that a separately installed package has its own permissions.
replace(main,
    '''else registerReceiver(changed,new IntentFilter("de.boyka.kallebuddy.CHANGED"));}''',
    '''else registerReceiver(changed,new IntentFilter("de.boyka.kallebuddy.CHANGED"));
        handler.postDelayed(()->{
          if(!isFinishing() && !Store.prefs(this).getBoolean("popupGuideSeen305",false) && !PopupCheck.ready(this)){
            Store.prefs(this).edit().putBoolean("popupGuideSeen305",true).apply();
            PopupCheck.guide(this);
          }
        },700);
    }''')

# Always-accessible status button. Not just a silent Settings checkbox.
replace(main,
    'root.addView(top);Ui.gap(root,10);',
    '''root.addView(top);Ui.gap(root,10);
        if(!PopupCheck.ready(this)){
          root.addView(Ui.button(this,"⚠ POP-UPS EINRICHTEN / STATUS",true,()->PopupCheck.guide(this)));
          Ui.gap(root,12);
        }''')

# Clear, directly usable tests for two DIFFERENT Android features.
replace(main,
    'root.addView(Ui.button(this,"TON UND POP-UP PRÜFEN",false,()->AlarmService.preview(this)));Ui.gap(root,12);',
    '''root.addView(Ui.button(this,"1. BENACHRICHTIGUNGS-POP-UP TESTEN",false,()->AlarmService.preview(this)));Ui.gap(root,10);
        root.addView(Ui.button(this,"2. SCHWEBENDES MISSIONSFENSTER TESTEN",true,()->PopupCheck.overlayPreview(this)));Ui.gap(root,10);
        root.addView(Ui.button(this,"POP-UP-STATUS / HILFE",false,()->PopupCheck.guide(this)));Ui.gap(root,12);''')

# Explicit automatic confirmation after snoozing from a notification action.
replace(alarm,
    ' static String diagnostics(Context c){',
    ''' static void snoozed(Context c,Mission m){
    if(m==null || !Scheduler.reminders(c))return;
    NotificationManager nm=c.getSystemService(NotificationManager.class);
    nm.createNotificationChannel(channel());
    if(!nm.areNotificationsEnabled())return;
    int humor=SnoozeReaction.effectiveHumor(Store.prefs(c).getInt("humor",1),
        Store.prefs(c).getBoolean("vulgar",false));
    String message=SnoozeReaction.message(m,humor);
    Notification notice=new Notification.Builder(c,CHANNEL)
        .setSmallIcon(R.drawable.ic_mission)
        .setContentTitle(SnoozeReaction.title(m.snoozeCount)+" / "+m.title)
        .setContentText(SnoozeReaction.line(m.snoozeCount,humor))
        .setStyle(new Notification.BigTextStyle().bigText(message))
        .setContentIntent(Scheduler.open(c,m.id))
        .setCategory(Notification.CATEGORY_REMINDER)
        .setPriority(Notification.PRIORITY_HIGH)
        .setVisibility(Notification.VISIBILITY_PRIVATE)
        .setAutoCancel(true)
        .setTimeoutAfter(12000)
        .build();
    try{nm.notify(m.id+500000,notice);}catch(SecurityException ex){
        android.util.Log.w("Kalle","No POST_NOTIFICATIONS permission for snooze confirmation",ex);
    }
 }
 static String diagnostics(Context c){''')

replace(store,
    '''  CompanionService.feedback(c,line);
  KalleWidget.updateAll(c);''',
    '''  CompanionService.feedback(c,line);
  // On a notification action Android cannot silently open an Activity.
  // Show the escalated Kalle response as a separate heads-up notification.
  AlarmService.snoozed(c,m);
  KalleWidget.updateAll(c);''')

replace(gradle,"applicationId 'de.boyka.kallebuddy.test304'",
              "applicationId 'de.boyka.kallebuddy.test305'")
replace(gradle,"versionCode 30009","versionCode 30010")
replace(gradle,"versionName '3.0.4'","versionName '3.0.5-test'")
replace(manifest,'android:versionCode="30009" android:versionName="3.0.4"',
                 'android:versionCode="30010" android:versionName="3.0.5-test"')
replace(manifest,"Kalle 3.0.4 Test","Kalle 3.0.5 Pop-up-Test",2)
replace(main,"KALLE / CHAOSBUDDY 3.0.3","KALLE / CHAOSBUDDY 3.0.5")

(project/"CHANGES-3.0.5-POPUPS.md").write_text(
"""# Chaosbuddy 3.0.5 – Pop-up Repair TEST
- Based on the actual upgraded 3.0.4 source, not the discarded 3.3 Revier.
- First-launch permission diagnostic specifically for newly installed test variants.
- Persistent accessible setup button on home when pop-up settings are incomplete.
- Two distinct live tests: Android heads-up notification + 10s real TYPE_APPLICATION_OVERLAY window.
- Escalating heads-up notification on snooze, including notification action; same mission data logic.
- Original in-app escalating Kalle snooze dialog and animation left in place.
- No microphone or speech recognition added. No new background service.
- Test package 'de.boyka.kallebuddy.test305' so previous apps remain untouched.
- Android 15 / Samsung may suppress heads-up banners if user disables channel pop-ups,
  foreground permissions, DND etc; bypassing OS restrictions is NOT possible.
- Never copy any signing material to GitHub. Build debug-signed only.
""",encoding="utf-8")
print("Patch 3.0.5 pop-up repair done (notification + overlay diagnostics).")
