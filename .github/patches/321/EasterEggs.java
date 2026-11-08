package de.boyka.kallebuddy;

import android.content.Context;
import android.content.SharedPreferences;
import java.util.Calendar;

/** Discoverable, persistent, local-only secrets. Not a background scheduler. */
final class EasterEggs {
    private EasterEggs() {}
    private static final String[] IDS = {
        "sechs", "nervensaege", "stammkunde", "inventar",
        "nachtgeist", "fruehschicht", "zeltkontrolle", "feuerwehr",
        "leseratte", "anglerlatein", "schneemann", "szenenmarathon",
        "kanalwechsel", "pfandkoenig", "pfandimperium"
    };
    private static final String[] NAMES = {
        "Geheimer Tanz", "Nervensäge", "Dauergast", "Kalle-Inventar",
        "Nachtschicht", "Viel zu früh", "Zeltkontrolle", "Feuer frei",
        "Bildungsauftrag", "Anglerlatein", "Frostbeule", "Szenenspringer",
        "Alles schon gesehen", "Pfandkönig", "Pfandimperium"
    };
    private static final String[] HINTS = {
        "Kalle sechsmal sehr schnell antippen.",
        "Kalle insgesamt 15-mal antippen.",
        "Kalle insgesamt 40-mal antippen.",
        "Kalle insgesamt 100-mal antippen.",
        "Kalle nach Mitternacht besuchen.",
        "Kalle früh am Morgen wecken.",
        "Kalle beim Zelt erwischen.",
        "Das Lagerfeuer oder den Grill erwischen.",
        "Kalle beim Zeitunglesen stören.",
        "Kalle beim Angeln besuchen.",
        "Mit Kalle im Schnee spielen.",
        "Achtmal die Szene wechseln.",
        "Zwanzigmal die Szene wechseln.",
        "Drei virtuelle Pfandflaschen spenden.",
        "Zehn virtuelle Pfandflaschen spenden."
    };
    static int total(){return IDS.length;}
    static int unlocked(Context c){
        SharedPreferences p=Store.prefs(c);int n=0;
        for(String id:IDS)if(p.getBoolean("egg_"+id,false))n++;
        return n;
    }
    static String journal(Context c){
        SharedPreferences p=Store.prefs(c);
        StringBuilder s=new StringBuilder("GEHEIMNISSE  "+unlocked(c)+"/"+total()+"\n\n");
        for(int i=0;i<IDS.length;i++){
            boolean seen=p.getBoolean("egg_"+IDS[i],false);
            s.append(seen?"✓ ":"? ").append(seen?NAMES[i]:"Unentdeckt "+(i+1))
             .append("\n").append(seen?"Freigeschaltet":HINTS[i]).append("\n\n");
        }
        return s.toString();
    }
    private static String unlock(Context c,String id,String line){
        SharedPreferences p=Store.prefs(c);
        if(p.getBoolean("egg_"+id,false))return null;
        if(!p.edit().putBoolean("egg_"+id,true).commit())return null;
        return "★ GEHEIMNIS ENTDECKT ★\n"+line+"\n("+unlocked(c)+"/"+total()+")";
    }
    static String onTap(Context c,int fastTaps,KalleScene.Action observed){
        SharedPreferences p=Store.prefs(c);
        int taps=p.getInt("egg_total_taps",0)+1;
        p.edit().putInt("egg_total_taps",taps).commit();
        if(fastTaps==6){
            String x=unlock(c,"sechs","SECHSMAL?! Hast du Tourette im Zeigefinger? Hier ist dein verdammter Geheimtanz.");
            if(x!=null)return x;
        }
        int hour=Calendar.getInstance().get(Calendar.HOUR_OF_DAY);
        if(hour>=0&&hour<5){
            String x=unlock(c,"nachtgeist","Es ist mitten in der Nacht! Mein Schlafrhythmus hat dich jetzt offiziell angezeigt.");
            if(x!=null)return x;
        }
        if(hour>=5&&hour<8){
            String x=unlock(c,"fruehschicht","Wer morgens so früh freiwillig aufsteht, muss ein ernstes Problem haben.");
            if(x!=null)return x;
        }
        if(observed==KalleScene.Action.TENT){
            String x=unlock(c,"zeltkontrolle","Zeltkontrolle?! Das ist kein Mietobjekt, du neugieriger Lappen!");
            if(x!=null)return x;
        }
        if(observed==KalleScene.Action.FIRE||observed==KalleScene.Action.BBQ){
            String x=unlock(c,"feuerwehr","Brennt alles noch ordentlich? Gut. Meine Karriere als Feuerwehrmann ist damit erledigt.");
            if(x!=null)return x;
        }
        if(observed==KalleScene.Action.NEWSPAPER){
            String x=unlock(c,"leseratte","Laut Zeitung bin ich ein hoffnungsloser Fall. Immerhin steh ich mal in der Presse.");
            if(x!=null)return x;
        }
        if(observed==KalleScene.Action.FISH){
            String x=unlock(c,"anglerlatein","Heute hab ich einen Fisch gefangen. Er hat mich wieder freigelassen.");
            if(x!=null)return x;
        }
        if(observed==KalleScene.Action.SNOWMAN){
            String x=unlock(c,"schneemann","Den Schneemann hab ich eingestellt. Er ist der erste Mitarbeiter mit kühlem Kopf.");
            if(x!=null)return x;
        }
        if(taps>=100){
            String x=unlock(c,"inventar","HUNDERTMAL hast du mich angefasst! Jetzt bist du Teil der Inventarliste.");
            if(x!=null)return x;
        }
        if(taps>=40){
            String x=unlock(c,"stammkunde","40 Berührungen. Such dir ein Hobby, Alter. Oder bleib. Ich brauch Publikum.");
            if(x!=null)return x;
        }
        if(taps>=15)return unlock(c,"nervensaege","15-mal geklickt. Ich bin kein verdammter Aufzugknopf, Kollege.");
        return null;
    }
    static String onScene(Context c){
        SharedPreferences p=Store.prefs(c);
        int count=p.getInt("egg_scene_switches",0)+1;
        p.edit().putInt("egg_scene_switches",count).commit();
        if(count>=20){
            String s=unlock(c,"kanalwechsel","20-mal Szene gewechselt. Du hast Fernbedienungs-Sucht, mein Freund.");
            if(s!=null)return s;
        }
        if(count>=8)return unlock(c,"szenenmarathon","Acht Szenenwechsel. Kalle wurde inzwischen vom Tourismusamt verklagt.");
        return null;
    }
    static String onDonation(Context c){
        int count=Store.prefs(c).getInt("kalleDonations",0);
        if(count>=10){
            String s=unlock(c,"pfandimperium","Zehn virtuelle Pfandflaschen! Ich eröffne eine Bank. Aus Pappe.");
            if(s!=null)return s;
        }
        if(count>=3)return unlock(c,"pfandkoenig","Drei Pfandflaschen? Du bist jetzt mein inoffizieller Finanzminister.");
        return null;
    }
}