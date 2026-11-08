#!/usr/bin/env python3
"""Minimal CI patch for Kalle 3.1.1 calm-scene test APK.
The archived 3.1.0 source and original installed app are not changed.
"""
from pathlib import Path

root=Path("Kalle-Chaosbuddy-3.1.0")
assert (root/"settings.gradle").exists(), "Android project not extracted"

p=root/"app/src/main/java/de/boyka/kallebuddy/WorldViews.java"
source=p.read_text(encoding="utf-8")
old='''  else{int ms=WidgetRenderer.interval(c);RemoteViews flip=new RemoteViews(c.getPackageName(),ms==100?R.layout.widget_flipper_fast:ms==200?R.layout.widget_flipper_slow:R.layout.widget_flipper_normal);for(int scene=0;scene<WorldMotion.SCENES;scene++)for(int i=0;i<WorldMotion.STEPS;i++)flip.addView(R.id.widget_flipper,frame(c,widget,WorldMotion.at(program[scene],scene,i,Store.prefs(c).getInt("kalleSize",100),origin,range,baseline),field,true));stage.addView(R.id.world_motion_host,flip);}'''
new='''  else{
   // Activity lasts 64s; each activity's 64 motion frames still play at 100-200ms.
   // Previously all 4 activities shared one flipper, changing after 6.4-12.8s.
   int ms=WidgetRenderer.interval(c);
   RemoteViews activities=new RemoteViews(c.getPackageName(),R.layout.widget_scene_flipper);
   for(int scene=0;scene<WorldMotion.SCENES;scene++){
    RemoteViews motion=new RemoteViews(c.getPackageName(),ms==100?R.layout.widget_flipper_fast:ms==200?R.layout.widget_flipper_slow:R.layout.widget_flipper_normal);
    for(int i=0;i<WorldMotion.STEPS;i++)
     motion.addView(R.id.widget_flipper,frame(c,widget,WorldMotion.at(program[scene],scene,i,Store.prefs(c).getInt("kalleSize",100),origin,range,baseline),field,true));
    activities.addView(R.id.widget_scene_flipper,motion);
   }
   stage.addView(R.id.world_motion_host,activities);
  }'''
assert source.count(old)==1, f"WorldViews animation pattern not found (count={source.count(old)})"
p.write_text(source.replace(old,new),encoding="utf-8")

layout=root/"app/src/main/res/layout/widget_scene_flipper.xml"
assert not layout.exists(), "Scene flipper already exists"
layout.write_text('''<?xml version="1.0" encoding="utf-8"?>
<ViewFlipper xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/widget_scene_flipper"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:autoStart="true"
    android:flipInterval="64000"
    android:clipChildren="true"
    android:clipToPadding="true" />
''',encoding="utf-8")

gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
for oldval,newval in [
    ("applicationId 'de.boyka.kallebuddy'","applicationId 'de.boyka.kallebuddy.test311'"),
    ("versionCode 30100","versionCode 30101"),
    ("versionName '3.1.0'","versionName '3.1.1-test'"),
]:
    assert g.count(oldval)==1, f"Gradle expected {oldval}"
    g=g.replace(oldval,newval)
gradle.write_text(g,encoding="utf-8")

manifest=root/"app/src/main/AndroidManifest.xml"
m=manifest.read_text(encoding="utf-8")
assert m.count("Kalle – Chaosbuddy 3.1.0")==1
manifest.write_text(m.replace("Kalle – Chaosbuddy 3.1.0","Kalle 3.1.1 Test (ruhig)"),encoding="utf-8")
print("Calm scene patch OK: 64-second activities, existing movement speed, test311 ID")
