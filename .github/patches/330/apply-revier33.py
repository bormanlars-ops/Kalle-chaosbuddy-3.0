#!/usr/bin/env python3
"""Patch the original 3.1.0 source. No private certificate or signing backup involved."""
from pathlib import Path

root=Path("Kalle-Chaosbuddy-3.1.0")
assert (root/"settings.gradle").is_file()
java=root/"app/src/main/java/de/boyka/kallebuddy"
assert (java/"MainActivity.java").is_file()

def replace(path,old,new,n=1):
    s=path.read_text(encoding="utf-8")
    count=s.count(old)
    if count != n: raise RuntimeError(f"{path}: {old[:85]!r} expected {n}, got {count}")
    path.write_text(s.replace(old,new,n),encoding="utf-8")

widget=java/"WorldViews.java"
replace(widget,
    'KalleScene.Action[] program=WidgetStory.select(c,widget,java.util.Calendar.getInstance());if(!still)WorldAssets.configure(c,program,origin);',
    'KalleScene.Action[] program=WidgetStory.select(c,widget,java.util.Calendar.getInstance());')
old_start='  if(still)stage.addView(R.id.world_motion_host,frame(c,widget,WorldMotion.at('
old_end='stage.addView(R.id.world_motion_host,flip);}'
source=widget.read_text(encoding="utf-8")
a=source.index(old_start)
b=source.index(old_end,a)+len(old_end)
stable='''  // Stable one-frame launcher presentation. No ViewFlipper, no resetting/teleporting.
  // User taps and scheduled widget refreshes may choose another calm pose.
  KalleScene.Action pose=program[0];
  if(pose==KalleScene.Action.WALK || pose==KalleScene.Action.CART || pose==KalleScene.Action.TURN)
      pose=KalleScene.Action.STAND;
  WorldMotion.Frame snapshot=WorldMotion.at(pose,0,32,Store.prefs(c).getInt("kalleSize",100),origin,range,baseline);
  snapshot.pose=pose;
  snapshot.spriteStep=2;
  stage.addView(R.id.world_motion_host,frame(c,widget,snapshot,field,show));'''
widget.write_text(source[:a]+stable+source[b:],encoding="utf-8")

main=java/"MainActivity.java"
replace(main,'"KALLE / CHAOSBUDDY 3.1.0"','"KALLE / CHAOSBUDDY 3.3.0"')
replace(main,
 'root.addView(Ui.button(this,"KALLES 4×4-REVIER HINZUFÜGEN",false,()->KalleWidget.pin(this)));Ui.gap(root,12);',
 '''root.addView(Ui.button(this,"KALLES 4×4-REVIER HINZUFÜGEN",false,()->KalleWidget.pin(this)));Ui.gap(root,12);
            root.addView(Ui.accentButton(this,"KALLES LEBENDIGES REVIER OEFFNEN",Ui.GREEN,()->startActivity(new Intent(this,KalleRevierActivity.class))));Ui.gap(root,12);''')
replace(main,
 'root.addView(Ui.button(this,"4×4-REVIER HINZUFÜGEN",false,()->KalleWidget.pin(this)));Ui.gap(root,16);',
 '''root.addView(Ui.button(this,"4×4-REVIER HINZUFÜGEN",false,()->KalleWidget.pin(this)));Ui.gap(root,10);
        root.addView(Ui.button(this,"KALLES LEBENDIGES REVIER SPIELEN",true,()->startActivity(new Intent(this,KalleRevierActivity.class))));Ui.gap(root,16);''')
replace(main,
 'choose("Laufgeschwindigkeit","speed"',
 'choose("Laufgeschwindigkeit im geoeffneten Revier","speed"')
replace(main,
 "Figur antippen: direkte Reaktion. Szene: optionale Handsteuerung. Kalle läuft zu festen Lagerplätzen, benutzt Gegenstände und geht weiter. Sprechblasen erscheinen gelegentlich und verschwinden nach vier Sekunden. Bewegung und Tiefe bleiben im Widget. Das vorbereitete Programm wird bei Ereignissen und regulären Systemupdates erneuert. Ruhezeiten werden beim nächsten Inhaltsupdate berücksichtigt.",
 "Im Homescreen-Widget bleibt Kalle absichtlich ruhig: keine endlose Laufanimation und kein Zurueckspringen mehr. Tippen auf die Figur oder Szenenwechsel aktualisieren seine Pose. In KALLES LEBENDIGEM REVIER laeuft er hingegen stufenlos, handelt eigenstaendig und erlebt sichtbare, speicherbare Geheimnisse. Keine Spracheingabe.")
replace(main,
 'Kalle wohnt ausschließlich in seinem nativen 4×4-Widget. Für die Figur ist keine Overlay-Erlaubnis nötig. Nur das optionale Missionsfenster nutzt sie. Android-Benachrichtigungen und deren Ton bleiben unabhängig vom Widget.',
 'Kalle erscheint im nativen 4×4-Widget und im neuen, nur auf Wunsch geoeffneten Revier. Keine Overlay-Erlaubnis fuer die Figur noetig. Missionen und Erinnerungen bleiben separat aktiv.')

widget_dialog=java/"WidgetInteractionActivity.java"
replace(widget_dialog,
 'root.addView(Ui.button(this,"ZU DEN MISSIONEN",false',
 '''root.addView(Ui.button(this,"KALLES LEBENDIGES REVIER",true,()->{startActivity(new android.content.Intent(this,KalleRevierActivity.class));finish();}));Ui.gap(root,10);
  root.addView(Ui.button(this,"ZU DEN MISSIONEN",false''')

manifest=root/"app/src/main/AndroidManifest.xml"
replace(manifest,'android:versionCode="30100" android:versionName="3.1.0"','android:versionCode="30300" android:versionName="3.3.0-test"')
replace(manifest,'android:label="Kalle – Chaosbuddy 3.1.0"','android:label="Kalle 3.3 Revier-Test"')
replace(manifest,'<activity android:name=".MainActivity"',
 '''<activity android:name=".KalleRevierActivity" android:exported="false" android:screenOrientation="sensorLandscape" />
        <activity android:name=".MainActivity"''')

gradle=root/"app/build.gradle"
replace(gradle,"applicationId 'de.boyka.kallebuddy'","applicationId 'de.boyka.kallebuddy.revier33'")
replace(gradle,"versionCode 30100","versionCode 30300")
replace(gradle,"versionName '3.1.0'","versionName '3.3.0-test'")

# UI original min SDK and all mission logic preserved; no unrequested voice feature.
(root/"CHANGES-3.3.0-REVIER.md").write_text(
"""# Kalle Chaosbuddy 3.3.0 – Revier Test

* Restores original 3.1.0 mission/weekly/statistics code.
* Widget: one calm snapshot. Removed the 256-frame flipper that reset position.
* User-opened landscape Revier: independent movement with delta-time, no coordinate reset.
* Tap radio, bin, manhole, bird or lamppost; visible actions and five connected visual mysteries.
* Secret discovery persisted locally in revier33 preferences.
* No voice input, microphone permission, or speech recognition.
* Test package de.boyka.kallebuddy.revier33 installs separately.
* Original signing backup is never read, copied, or committed.
* In-app animation is active only while the Revier Activity is visible.
* Android launcher may refresh or defer widget snapshots; widget is not a running game.
* Existing four failing legacy tests not claimed fixed.
""",encoding="utf-8")
print("3.3.0 patch OK: widget loop removed, in-app Revier integrated, no voice.")
