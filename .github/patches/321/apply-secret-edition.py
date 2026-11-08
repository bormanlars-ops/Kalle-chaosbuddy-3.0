#!/usr/bin/env python3
"""Apply 3.2.1 SECRET EDITION after the archived 3.1.0 source and 3.1.1 calm patch.
Never reads any signers' backup; uses the standard ephemeral GitHub debug key.
"""
from pathlib import Path

root = Path("Kalle-Chaosbuddy-3.1.0")
source = root / "app/src/main/java/de/boyka/kallebuddy"
assert (source / "WidgetState.java").is_file(), "Source ZIP must be extracted first"
assert (source / "WorldSpeech.java").is_file(), "Expected source missing"
assert (root / "app/src/main/res/layout/widget_scene_flipper.xml").exists(), "Run calm-scene patch first"

def rep(path, old, new, count=1):
    s=path.read_text(encoding="utf-8")
    actual=s.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} occurrences of {old[:80]!r}, got {actual}")
    path.write_text(s.replace(old,new,count),encoding="utf-8")

widget=source/"WidgetState.java"
rep(widget, '''  if(count>=4){if(count==4)''',
'''  KalleScene.Action observed=action(c,id);
  String surprise=EasterEggs.onTap(c,count,observed);
  if(surprise!=null){
    if(count==6)setAction(c,id,KalleScene.Action.DANCE);
    p.edit().putString(key(id,"text"),surprise).commit();
    WorldSpeech.event(c,id);
    return surprise;
  }
  if(count>=4){if(count==4)''')
rep(widget, 'setAction(c,id,v[(n+i)%v.length]);return;}',
'''setAction(c,id,v[(n+i)%v.length]);
   String surprise=EasterEggs.onScene(c);
   if(surprise!=null){prefs(c).edit().putString(key(id,"text"),surprise).commit();WorldSpeech.event(c,id);}
   return;}''')
rep(widget, '''prefs(c).edit().putString(key(id,"text"),yes?"Ehrenmensch! Eine virtuelle Pfandflasche für meinen Ruhestand. Keine echte Zahlung, Chef.":"Okay, Chef. Meine virtuelle Pfandkasse hat Geduld.").commit();}''',
'''prefs(c).edit().putString(key(id,"text"),yes?"Ehrenmensch! Eine virtuelle Pfandflasche für meinen Ruhestand. Keine echte Zahlung, Chef.":"Okay, Chef. Meine virtuelle Pfandkasse hat Geduld.").commit();
  if(yes){String surprise=EasterEggs.onDonation(c);
   if(surprise!=null){prefs(c).edit().putString(key(id,"text"),surprise).commit();WorldSpeech.event(c,id);}}
 }''')

# Add the actual discovery collection to both widget-dialog and the full app.
dialog=source/"WidgetInteractionActivity.java"
rep(dialog, '''root.addView(Ui.button(this,"ZU DEN MISSIONEN",false''',
'''root.addView(Ui.button(this,"★ GEHEIMNISSE  "+EasterEggs.unlocked(this)+"/"+EasterEggs.total(),false,
   ()->new AlertDialog.Builder(this).setTitle("KALLES GEHEIME SAMMLUNG").setMessage(EasterEggs.journal(this)).setPositiveButton("Schließen",null).show()));
  Ui.gap(root,9);
  root.addView(Ui.button(this,"ZU DEN MISSIONEN",false''')

activity=source/"MainActivity.java"
rep(activity, 'KALLE / CHAOSBUDDY 3.1.0','KALLE / CHAOSBUDDY 3.2.1 · GEHEIMNISSE')
rep(activity, '''root.addView(Ui.button(this,"DATEN EXPORTIEREN"''',
'''root.addView(Ui.button(this,"★ GEHEIMNISSE  "+EasterEggs.unlocked(this)+"/"+EasterEggs.total(),false,()->new AlertDialog.Builder(this).setTitle("KALLES GEHEIME SAMMLUNG").setMessage(EasterEggs.journal(this)).setPositiveButton("Schließen",null).show()));Ui.gap(root,10);
        root.addView(Ui.button(this,"DATEN EXPORTIEREN"''')
rep(activity, '''Figur antippen: direkte Reaktion. Szene: optionale Handsteuerung. Kalle läuft zu festen Lagerplätzen, benutzt Gegenstände und geht weiter. Sprechblasen erscheinen gelegentlich und verschwinden nach vier Sekunden. Bewegung und Tiefe bleiben im Widget. Das vorbereitete Programm wird bei Ereignissen und regulären Systemupdates erneuert. Ruhezeiten werden beim nächsten Inhaltsupdate berücksichtigt.''',
'''Figur antippen: direkte Reaktion. Schnell sechs Mal tippen, Kalle bei seltenen Tätigkeiten erwischen oder die Szene wechseln: 15 geheime Entdeckungen warten. Sammelbuch in den Einstellungen. Szenen dauern rund eine Minute. Sprechblasen bleiben kurz sichtbar. Widgets unterliegen den Android-Hintergrundgrenzen.''')
rep(activity, '''Keine Spracheingabe.''',
'''Keine Spracheingabe. Missionen werden ausschließlich per Tastatur angelegt.''')

# More varied self-talk. No external service or unnecessary permissions.
speech=source/"WorldSpeech.java"
rep(speech, '''   "Hab mich kurz verlaufen. In meinem eigenen Revier. Frag nicht."''',
'''   "Hab mich kurz verlaufen. In meinem eigenen Revier. Frag nicht.",
   "Meine Socken haben einen Betriebsrat gegründet. Ich bin rausgeflogen.",
   "Ich hab einen Job gefunden: professioneller Pausenprüfer.",
   "Der Müllcontainer hat mich heute wieder nicht reingelassen.",
   "Meine gute Laune ist irgendwo zwischen Pfandautomat und Bushaltestelle verschwunden.",
   "Ich wollte aufräumen. Dann musste ich erstmal meine Ausreden sortieren.",
   "Mein Vermieter nennt das Verwahrlosung. Ich nenne das Industrial Design.",
   "Die Möwen haben meinen Einkaufszettel gefressen. War eh nur Bier und Brot.",
   "Meine Zimmerpflanze ist abgehauen. Verständlich.",
   "Kalle, warum bist du so? Gute Frage. Nächste!",
   "Die Fernbedienung hat eine höhere Lebenserwartung als mein Businessplan.",
   "Wenn Faulheit Strom erzeugen würde, wäre ich Großkraftwerk.",
   "Ich hab überlegt zu kündigen. Dann fiel mir ein: Ich hab keinen Job.",
   "Der Campingstuhl knarzt. Wahrscheinlich vor Enttäuschung.",
   "Die Taube hat mein Frühstück geklaut. Ich hab ihr den Mietvertrag geschickt.",
   "Heute bin ich fast pünktlich aufgewacht. Für gestern.",
   "Mein Sparschwein hat Insolvenz angemeldet. Die Sau kennt sich aus.",
   "Ich brauche einen Urlaub. Von meinem Urlaub.",
   "Zehn Minuten Sport? Schon beim Gedanken habe ich Muskelkater.",
   "Ich hab den Wetterbericht gelesen. Auch das Wetter hat keinen Bock.",
   "Die Mülltonne und ich haben denselben Karriereberater.",
   "Ralle sagt, ich soll was aus meinem Leben machen. Er steht im selben Hinterhof.",
   "Kaffee ist mein Sicherheitsabstand zur Gesellschaft.",
   "Mein Wecker und ich führen seit Jahren einen kalten Krieg.",
   "Ich habe Disziplin bestellt. Paket kam nie an."
''')

# The archive remains unchanged. The debug preview has its own package name.
gradle=root/"app/build.gradle"
rep(gradle,"applicationId 'de.boyka.kallebuddy.test311'","applicationId 'de.boyka.kallebuddy.test321'")
rep(gradle,"versionCode 30101","versionCode 30201")
rep(gradle,"versionName '3.1.1-test'","versionName '3.2.1-secret-test'")
manifest=root/"app/src/main/AndroidManifest.xml"
rep(manifest,"Kalle 3.1.1 Test (ruhig)","Kalle 3.2.1 Geheimnisse",2)

# Counters are included in existing backup export/import (all primitive settings).
backup=source/"Backup.java"
rep(backup,'"homeTalkSeconds","humor"','"homeTalkSeconds","egg_total_taps","egg_scene_switches","humor"')

# Explicit source audit, catches accidental regression from earlier 3.2 experiment.
for p in source.glob("*.java"):
    if p.name=="MainActivity.java":
        check=p.read_text(encoding="utf-8").lower()
        for disallowed in ("recognizerintent","mission diktieren","spokencommandfield","action_recognize_speech","spracheingabe per android-dienst"):
            assert disallowed not in check, f"Voice was not fully removed: {disallowed}"

(root/"CHANGES-3.2.1-SECRET-TEST.md").write_text(
"""# Kalle Chaosbuddy 3.2.1 – Easter Egg Edition
- 15 one-time Easter eggs with persistent progress, contextual activity, time, tap and scene-switch triggers.
- New journal in settings and widget interaction screen; hints for undiscovered secrets.
- 24 new ambient quips with existing randomization/cooldowns.
- Previous calm scene fix: ~64 seconds per activity; movement loops independently.
- NO voice input, microphone usage or speech-recognition integration.
- Unique Android debug package: de.boyka.kallebuddy.test321.
- No signing backup included or used. Original apps never overwritten.
- Some legacy tests are known to fail; verify actual behavior on Samsung launcher.
""",encoding="utf-8")
print("Chaosbuddy 3.2.1: 15 eggs, new journal, no voice, unique debug package.")
