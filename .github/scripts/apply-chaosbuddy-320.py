#!/usr/bin/env python3
"""Safe, reproducible public source patch. No signing material is read or copied."""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
source=root/'app/src/main/java/de/boyka/kallebuddy'
layouts=root/'app/src/main/res/layout'
assert (source/'MainActivity.java').is_file()

def replace(path,old,new,n=1):
    s=path.read_text(encoding='utf-8')
    hits=s.count(old)
    assert hits==n, f'{path.name}: expected {n} instances, found {hits}: {old[:80]}'
    path.write_text(s.replace(old,new),encoding='utf-8')

# Native two-level view-flipper. The inner cycle remains smooth; outer sequence
# advances activities no faster than the explicit 45/60/90-second setting.
views=source/'WorldViews.java'
old='''  else{int ms=WidgetRenderer.interval(c);RemoteViews flip=new RemoteViews(c.getPackageName(),ms==100?R.layout.widget_flipper_fast:ms==200?R.layout.widget_flipper_slow:R.layout.widget_flipper_normal);for(int scene=0;scene<WorldMotion.SCENES;scene++)for(int i=0;i<WorldMotion.STEPS;i++)flip.addView(R.id.widget_flipper,frame(c,widget,WorldMotion.at(program[scene],scene,i,Store.prefs(c).getInt("kalleSize",100),origin,range,baseline),field,true));stage.addView(R.id.world_motion_host,flip);}'''
new='''  else{
   // Each room activity is held for 45-90 seconds; pose animation loops inside.
   int ms=WidgetRenderer.interval(c);
   int dwell=WorldPacing.seconds(Store.prefs(c).getInt("sceneSeconds",60));
   int outer=dwell==45?R.layout.world_scene_45:dwell==90?R.layout.world_scene_90:R.layout.world_scene_60;
   RemoteViews sequence=new RemoteViews(c.getPackageName(),outer);
   for(int scene=0;scene<WorldMotion.SCENES;scene++){
    RemoteViews motion=new RemoteViews(c.getPackageName(),ms==100?R.layout.widget_flipper_fast:ms==200?R.layout.widget_flipper_slow:R.layout.widget_flipper_normal);
    for(int i=0;i<WorldMotion.STEPS;i++)motion.addView(R.id.widget_flipper,frame(c,widget,WorldMotion.at(program[scene],scene,i,Store.prefs(c).getInt("kalleSize",100),origin,range,baseline),field,true));
    sequence.addView(R.id.widget_scene_flipper,motion);
   }
   stage.addView(R.id.world_motion_host,sequence);
  }'''
replace(views,old,new)
for sec in (45,60,90):
    f=layouts/f'world_scene_{sec}.xml'
    assert not f.exists(),f'layout exists: {f}'
    f.write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<ViewFlipper xmlns:android="http://schemas.android.com/apk/res/android"
 android:id="@+id/widget_scene_flipper"
 android:layout_width="match_parent" android:layout_height="match_parent"
 android:autoStart="true" android:flipInterval="{sec*1000}"
 android:clipChildren="true" android:clipToPadding="true" />
''',encoding='utf-8')
(source/'WorldPacing.java').write_text('''package de.boyka.kallebuddy;
/** Clamped user-configurable scene dwell; no per-frame service or alarm. */
final class WorldPacing {
 static int seconds(int configured) {
  if(configured==45||configured==60||configured==90)return configured;
  return 60;
 }
}
''',encoding='utf-8')

activity=source/'MainActivity.java'
replace(activity,'import android.provider.Settings;','import android.provider.Settings;\nimport android.speech.RecognizerIntent;')
replace(activity,'    boolean addMissionOnOpen=false;','    boolean addMissionOnOpen=false;\n    EditText spokenCommandField;')
replace(activity,'        command.setSingleLine(false);command.setMaxLines(3);', '''        command.setSingleLine(false);command.setMaxLines(3);
        spokenCommandField=command;
        box.addView(Ui.button(this,"🎤 MISSION DIKTIEREN (OPTIONAL)",false,()->{
            Intent speech=new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
            speech.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
            speech.putExtra(RecognizerIntent.EXTRA_LANGUAGE,"de-DE");
            speech.putExtra(RecognizerIntent.EXTRA_PROMPT,"Kalle, morgen um 16:30 einkaufen …");
            try{startActivityForResult(speech,601);}catch(ActivityNotFoundException ex){
                new AlertDialog.Builder(this).setTitle("Spracheingabe nicht verfügbar")
                    .setMessage("Auf deinem Gerät ist kein kompatibler Spracherkennungsdienst installiert. Du kannst die Mission weiterhin eintippen.")
                    .setPositiveButton("OK",null).show();
            }
        }));''')
replace(activity,'    @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(result!=RESULT_OK||data==null||data.getData()==null)return;', '''    @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);
        if(request==601){
            if(result==RESULT_OK&&data!=null){
                ArrayList<String> recognized=data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
                if(recognized!=null&&!recognized.isEmpty()&&spokenCommandField!=null){
                    spokenCommandField.setText(recognized.get(0));
                    spokenCommandField.setSelection(spokenCommandField.length());
                    Toast.makeText(this,"Kalle hat mitgeschrieben. Bitte Text prüfen und BEFEHL PRÜFEN tippen.",Toast.LENGTH_LONG).show();
                }
            }
            return;
        }
        if(result!=RESULT_OK||data==null||data.getData()==null)return;''')
replace(activity,'choose("Laufgeschwindigkeit","speed",40,','choose("Szenenwechsel (45–90 Sekunden)","sceneSeconds",60,new String[]{"45 Sekunden","60 Sekunden (ruhig)","90 Sekunden (sehr ruhig)"},new int[]{45,60,90});choose("Sprechpausen im Widget","homeTalkSeconds",180,new String[]{"90 Sekunden","3 Minuten","5 Minuten","10 Minuten"},new int[]{90,180,300,600});choose("Laufgeschwindigkeit","speed",40,')
replace(activity,'KALLE / CHAOSBUDDY 3.1.0','KALLE / CHAOSBUDDY 3.2.0 TEST')
replace(activity,'Figur antippen: direkte Reaktion. Szene: optionale Handsteuerung. Kalle läuft zu festen Lagerplätzen, benutzt Gegenstände und geht weiter. Sprechblasen erscheinen gelegentlich und verschwinden nach vier Sekunden. Bewegung und Tiefe bleiben im Widget. Das vorbereitete Programm wird bei Ereignissen und regulären Systemupdates erneuert. Ruhezeiten werden beim nächsten Inhaltsupdate berücksichtigt.', 'Figur antippen: Reaktion. Verstecktes Geheimnis: schnell sechsmal tippen. Jede Szene dauert wahlweise 45, 60 oder 90 Sekunden; die Bewegung innerhalb der Szene läuft weiter. Sprechblasen verschwinden nach wenigen Sekunden. Android kann Widget-Aktualisierungen und Animationen im Hintergrund begrenzen.')
replace(activity,'Keine Spracheingabe.','Optionale Spracheingabe per Android-Dienst; Verfügbarkeit und Offline-Nutzung hängen vom Gerät ab. Nichts wird ohne Bestätigung gespeichert.')

state=source/'WidgetState.java'
replace(state,'  if(count>=4){if(count==4)', '''  if(count==6&&!Store.prefs(c).getBoolean("secretTapSeen",false)){
   Store.prefs(c).edit().putBoolean("secretTapSeen",true).commit();
   setAction(c,id,KalleScene.Action.DANCE);
   String secret="SECHSMAL?! Alter, du hast den geheimen Kalle-Tanz gefunden. Fass Gras an!";
   p.edit().putString(key(id,"text"),secret).commit();WorldSpeech.event(c,id);return secret;
  }
  if(count>=4){if(count==4)''')

backup=source/'Backup.java'
replace(backup,'"homeTalkSeconds","humor"','"homeTalkSeconds","sceneSeconds","humor"')
replace(backup,'"kalleAnimations"','"kalleAnimations","secretTapSeen"')

speech=source/'WorldSpeech.java'
replace(speech,'   "Hab mich kurz verlaufen. In meinem eigenen Revier. Frag nicht."', '''   "Hab mich kurz verlaufen. In meinem eigenen Revier. Frag nicht.",
   "Die Mülltonne nebenan hat einen besseren Überblick als mein Steuerberater.",
   "Ich hab den Vermieter angerufen. Der hat direkt aufgelegt. Läuft stabil.",
   "Wenn ich heute noch einmal produktiv werde, kündige ich mir selbst.",
   "Mein Campingstuhl hat Burnout. Seit ich ihn besitze.",
   "Die Tauben hier schulden mir drei Euro und ein Brötchen.",
   "Ich mach jetzt erstmal Pause von meiner letzten Pause.",
   "Ich hab einen Businessplan. Steht auf einem Kassenzettel.",
   "Ein Nachbar hat gefragt, ob ich arbeite. Ich hab den Kontakt abgebrochen.",
   "Das Lagerfeuer ist das einzige hier, das zuverlässig liefert.",
   "Meine Pfandtüte hat mehr Zukunftspläne als ich.",
   "Ich habe meine Socke gesucht. Die hat jetzt offenbar einen eigenen Mietvertrag.",
   "Keine Sorge, Chef. Mein Plan ist nur äußerlich beschissen."''')

# Clear debug preview identity; never touch original app installation or private signing key.
gradle=root/'app/build.gradle'
replace(gradle,"applicationId 'de.boyka.kallebuddy'","applicationId 'de.boyka.kallebuddy.test320'")
replace(gradle,'versionCode 30100; versionName \'3.1.0\'','versionCode 30200; versionName \'3.2.0-test\'')
manifest=root/'app/src/main/AndroidManifest.xml'
replace(manifest,'Kalle – Chaosbuddy 3.1.0','Kalle Chaosbuddy 3.2 Test',n=2)

# Testing and release notes bundled with source.
tests=root/'app/src/test/java/de/boyka/kallebuddy/WorldPacingTest.java'
tests.write_text('''package de.boyka.kallebuddy;
import org.junit.Test;
import static org.junit.Assert.*;
public final class WorldPacingTest {
 @Test public void validIntervals() {
  assertEquals(45,WorldPacing.seconds(45));
  assertEquals(60,WorldPacing.seconds(60));
  assertEquals(90,WorldPacing.seconds(90));
 }
 @Test public void invalidSettingsDefaultToSixty() {
  for(int i:new int[]{-1,0,1,25,44,61,100,999})assertEquals(60,WorldPacing.seconds(i));
 }
}
''',encoding='utf-8')
(root/'CHANGES-3.2.0-TEST.md').write_text('''# Chaosbuddy 3.2.0 TEST

- New scene pacing option: 45, 60, or 90 seconds. Inner motion stays animated without reselecting a whole new activity every few seconds.
- Optional Android speech recognition button for drafting missions. The result is ONLY inserted in the text field; existing preview/confirmation is mandatory. Availability/offline recognition depends on the Android speech provider.
- Widget speech interval selection: 90 seconds/3/5/10 minutes.
- 12 extra atmospheric quips, with existing repetition rules and priorities.
- Secret: tap the widget character six times rapidly to unlock a special one-time reaction.
- Separate debug package: de.boyka.kallebuddy.test320. No original app updates, no secret credentials used, no release signing.
- Caveat: Android widgets are launcher-owned, not real-time game surfaces. Device test required, including the new nested flipper on Samsung.
''',encoding='utf-8')
print('Applied v3.2.0 TEST patch; no signing material used')