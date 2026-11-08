package de.boyka.kallebuddy;

import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.ActivityInfo;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.os.Bundle;
import android.os.SystemClock;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import java.util.Calendar;
import java.util.Random;

/** A user-opened 2D street: continuous walking, choices, interactive objects, visual secrets.
 * No background animation loop or service. Lives only while this Activity is visible.
 */
public final class KalleRevierActivity extends Activity {
    private RevierView world;
    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN);
        getWindow().getDecorView().setSystemUiVisibility(5894|1024|512);
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE);
        world=new RevierView(this);
        setContentView(world);
    }
    @Override protected void onResume(){super.onResume();if(world!=null)world.resume();}
    @Override protected void onPause(){if(world!=null)world.pause();super.onPause();}

    static final class RevierView extends View {
        static final float W=360f,H=240f,GROUND=205f;
        static final int BIN=1,RADIO=2,HATCH=3,PIGEON=4,LAMP=5,FREE=0;
        static final String[] KEYS={"disco","pigeons","ghost","bunker","ufo"};
        static final String[] SECRET_NAMES={
            "Pfand-Rave","Taubenmafia","Der Muellgeist","Bunker unter der Gasse","Kalle wird entfuehrt"
        };
        static final String[] SECRET_HINTS={
            "Dreh am Radio, bis sogar Kalle tanzt.",
            "Stoer den gefiederten Gangster mehrmals.",
            "Die Tauben wissen, was in der Tonne wohnt.",
            "Der Muellgeist kennt den Gullideckel.",
            "Nach dem Rave hat die Strassenlampe Geheimnisse."
        };
        private final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);
        private final Random rng=new Random();
        private final Bitmap background;
        private final SharedPreferences prefs;
        private long last;
        private boolean running=false,walking=false,manual=false,journal=false;
        private int destination=FREE,lastDestination=-1,radioTaps=0,pigeonTaps=0;
        private float x=175,target=175,phase=0,freeTime=3,actionTime=0,bubbleTime=6,effectTime=0,clock=0;
        private int effect=0; // 1: disco, 2: birds, 3: ghost, 4: bunker, 5: UFO
        private boolean right=true;
        private String speech="Willkommen in meiner Gasse. Fass bloss nichts an, was lebt.";
        private KalleScene.Action action=KalleScene.Action.STAND;
        private final int[] discoveries=new int[5];

        RevierView(Context context){
            super(context);
            setLayerType(View.LAYER_TYPE_SOFTWARE,null);
            prefs=context.getSharedPreferences("revier33",0);
            x=clamp(prefs.getFloat("x",175),105,304);
            target=x;
            BitmapFactory.Options options=new BitmapFactory.Options();
            options.inScaled=false;options.inSampleSize=2;
            background=BitmapFactory.decodeResource(getResources(),R.drawable.widget_scene_background,options);
            setContentDescription("Kalles interaktives Revier mit fuenf visuellen Geheimnissen");
        }
        private float clamp(float n,float min,float max){return Math.max(min,Math.min(max,n));}
        void resume(){running=true;last=SystemClock.uptimeMillis();invalidate();}
        void pause(){running=false;prefs.edit().putFloat("x",x).apply();}
        private void say(String line,float duration){speech=line;bubbleTime=duration;}

        private void moveTo(float dest,int site,boolean byPlayer){
            dest=clamp(dest,105,304);
            target=dest;destination=site;manual=byPlayer;
            walking=Math.abs(target-x)>.3f;
            action=walking?KalleScene.Action.WALK:KalleScene.Action.STAND;
            actionTime=0f;
            freeTime=4f;
            if(!walking)arrive();
        }
        private float place(int site){
            switch(site){
                case BIN:return 114f;
                case RADIO:return 168f;
                case HATCH:return 225f;
                case PIGEON:return 287f;
                case LAMP:return 264f;
                default:return x;
            }
        }
        private void tick(){
            long now=SystemClock.uptimeMillis();
            float dt=clamp((now-last)/1000f,0f,.05f);last=now;clock+=dt;
            if(walking){
                float speed=clamp(33f+Store.prefs(getContext()).getInt("speed",40)*.25f,32f,54f);
                float previous=x;
                x=RevierMotion.step(x,target,speed,dt);
                right=x>=previous;
                phase+=dt*7.3f;
                if(RevierMotion.arrived(x,target)){x=target;walking=false;arrive();}
            }else if(actionTime>0){
                actionTime-=dt;
                phase+=dt*2.7f;
                if(actionTime<=0){action=KalleScene.Action.STAND;freeTime=3f+rng.nextFloat()*4f;}
            }else{
                phase+=dt*1.3f;
                freeTime-=dt;
                if(freeTime<=0)automaticChoice();
            }
            if(bubbleTime>0)bubbleTime-=dt;
            if(effectTime>0){effectTime-=dt;if(effectTime<=0){effect=0;effectTime=0;}}
        }
        private void automaticChoice(){
            if(rng.nextFloat()<.7f){
                int[] options={BIN,RADIO,HATCH,PIGEON,LAMP};
                int site=options[rng.nextInt(options.length)];
                if(site==lastDestination)site=options[(site+rng.nextInt(4)+1)%options.length];
                moveTo(place(site),site,false);
            }else{
                moveTo(105+rng.nextFloat()*199,FREE,false);
                say(new String[]{
                    "Ich mach meine Runde. Hausmeister von gar nichts, quasi.",
                    "Einmal die Gasse ablaufen. Mehr Bewegung als mein Konto.",
                    "Da hinten liegt bestimmt noch Pfand. Oder Hoffnungslosigkeit."
                }[rng.nextInt(3)],3.5f);
            }
        }
        private void arrive(){
            int site=destination;destination=FREE;
            if(site!=FREE)use(site,manual);
            else {action=KalleScene.Action.LOOK;actionTime=2f;freeTime=3f;}
        }
        private boolean found(String key){return prefs.getBoolean("secret_"+key,false);}
        private int foundCount(){int count=0;for(String key:KEYS)if(found(key))count++;return count;}
        private void secret(int id,String line){
            effect=id;effectTime=8.5f;
            String key=KEYS[id-1];
            boolean newOne=!found(key);
            if(newOne)prefs.edit().putBoolean("secret_"+key,true).apply();
            say((newOne?"GEHEIMNIS ENTDECKT: "+SECRET_NAMES[id-1]+"! ":"")+line,7.8f);
            action=id==1?KalleScene.Action.DANCE:id==3?KalleScene.Action.ANNOY:KalleScene.Action.LOOK;
            actionTime=6f;
        }
        private void use(int site,boolean byPlayer){
            lastDestination=site;
            switch(site){
                case BIN:
                    action=KalleScene.Action.CART;
                    if(byPlayer&&found("pigeons"))secret(3,"Die Tonne spricht! Sie fordert jetzt sogar Nebenkosten.");
                    else say("Das ist nicht Muell. Das ist mein Wertstoffdepot.",4f);
                    break;
                case RADIO:
                    action=KalleScene.Action.DANCE;
                    if(byPlayer&&++radioTaps>=3)secret(1,"Der Kiosk-Rave laeuft. Die Nachbarn rufen die Sittenpolizei.");
                    else say(byPlayer?"Neuer Sender, dieselben drei schlechten Lieder.":"Musik an. Gehirn aus.",4f);
                    break;
                case HATCH:
                    action=KalleScene.Action.LOOK;
                    if(byPlayer&&found("ghost"))secret(4,"Unter der Gasse: Mein geheimer Keller! Die Miete ist trotzdem zu hoch.");
                    else say("Gullideckel. Ich glaube, darunter wohnt mein Kreditberater.",4f);
                    break;
                case PIGEON:
                    action=KalleScene.Action.ANNOY;
                    if(byPlayer&&++pigeonTaps>=2)secret(2,"Die Tauben haben einen Schutzgeldring. Eine klaut meinen Keks!");
                    else say("Bodo, du gefiederter Parkscheinautomat! Finger weg vom Pfand!",4f);
                    break;
                case LAMP:
                    action=KalleScene.Action.LOOK;
                    if(byPlayer&&found("disco"))secret(5,"Die Ausserirdischen holen mich. Selbst im Weltall gibt es Mahnungen.");
                    else say("Laterne funktioniert. Anders als mein Lebensplan.",4f);
                    break;
                default:action=KalleScene.Action.STAND;
            }
            if(actionTime<=0)actionTime=3.6f+rng.nextFloat()*1.2f;
        }
        private void tapActor(){
            walking=false;action=KalleScene.Action.ANNOY;actionTime=2.4f;freeTime=3f;
            say(new String[]{
                "Kollege, das ist mein Arm. Kein Klingelknopf.",
                "Ich hab schon genug Beruehrungspunkte mit dem Jobcenter!",
                "Tipp auf die Gegenstaende. Ich bin kein Touchscreen-Hamster.",
                "Wolltest du mich umarmen? Dann kauf mir wenigstens eine Brezel."
            }[rng.nextInt(4)],3.2f);
        }
        @Override public boolean onTouchEvent(MotionEvent e){
            if(e.getAction()!=MotionEvent.ACTION_UP)return true;
            float scale=Math.min(getWidth()/W,getHeight()/H);
            float px=(e.getX()-(getWidth()-W*scale)/2f)/scale;
            float py=(e.getY()-(getHeight()-H*scale)/2f)/scale;
            if(journal){journal=false;invalidate();return true;}
            if(py<41){
                if(px>=290){((Activity)getContext()).finish();return true;}
                if(px>=187){journal=true;invalidate();return true;}
            }
            if(px>=18&&px<=116&&py>=112&&py<=210){moveTo(place(BIN),BIN,true);}
            else if(px>=117&&px<=165&&py>=155&&py<=204){moveTo(place(RADIO),RADIO,true);}
            else if(px>=206&&px<=252&&py>=175&&py<=212){moveTo(place(HATCH),HATCH,true);}
            else if(px>=279&&px<=328&&py>=138&&py<=199){moveTo(place(PIGEON),PIGEON,true);}
            else if(px>=256&&px<=300&&py>=54&&py<=145){moveTo(place(LAMP),LAMP,true);}
            else if(Math.abs(px-x)<35&&py>=95&&py<=211){tapActor();}
            else if(py>94&&py<210){moveTo(px,FREE,true);}
            invalidate();return true;
        }

        @Override protected void onDraw(Canvas raw){
            super.onDraw(raw);
            if(running)tick();
            raw.drawColor(Color.BLACK);
            float scale=Math.min(getWidth()/W,getHeight()/H);
            float dx=(getWidth()-W*scale)/2f,dy=(getHeight()-H*scale)/2f;
            raw.save();raw.translate(dx,dy);raw.scale(scale,scale);
            p.setStyle(Paint.Style.FILL);p.setColor(Color.WHITE);p.setAlpha(255);
            raw.drawBitmap(background,null,new RectF(0,0,W,H),p);
            drawStreet(raw);
            drawCharacter(raw);
            drawEffects(raw);
            drawHud(raw);
            if(journal)drawJournal(raw);
            raw.restore();
            if(running)postInvalidateDelayed(33);
        }
        private void box(Canvas c,float l,float t,float r,float b,int color,float radius){
            p.setStyle(Paint.Style.FILL);p.setColor(color);c.drawRoundRect(l,t,r,b,radius,radius,p);
        }
        private void text(Canvas c,String value,float x,float y,float sp,int color){
            p.setColor(color);p.setTextSize(sp);p.setTypeface(android.graphics.Typeface.create("sans-serif",android.graphics.Typeface.BOLD));
            p.setStyle(Paint.Style.FILL);c.drawText(value,x,y,p);
        }
        private void drawStreet(Canvas c){
            // Three props are added to the existing alley artwork; all have usable hit regions.
            box(c,118,166,155,198,0xff574a38,5);box(c,120,167,153,185,0xff89806a,3);
            box(c,124,172,148,183,0xff222f34,2);
            text(c,"FM",128,181,6,0xffb8cf9d);
            p.setColor(0xffe8b85f);c.drawCircle(146,192,2,p);
            p.setColor(0xff15181a);c.drawOval(208,186,255,204,p);
            p.setStyle(Paint.Style.STROKE);p.setColor(0xffa6a18c);p.setStrokeWidth(3);
            c.drawOval(208,186,255,204,p);p.setStyle(Paint.Style.FILL);
            p.setColor(0xffc0c3c8);c.drawOval(291,172,318,187,p);
            p.setColor(0xff87909e);c.drawOval(293,173,316,184,p);
            p.setColor(0xffddd9c4);c.drawCircle(307,172,8,p);
            p.setColor(0xffedb361);c.drawOval(313,174,324,178,p);
            p.setColor(Color.BLACK);c.drawCircle(310,171,1.5f,p);
            p.setColor(0x99716844);c.drawOval(x-23,200,x+23,209,p);
            if(effect==4&&effectTime>0){
                box(c,212,177,255,203,0xff061f22,3);
                p.setColor(0xff82ccb0);p.setStrokeWidth(1.5f);
                for(int i=0;i<4;i++)c.drawLine(220,182+i*5,234,182+i*5,p);
                text(c,"BUNKER",217,195,7,0xffe3ce8e);
            }
            if(effect==5&&effectTime>0){
                p.setColor(0x55aa99ff);
                Path beam=new Path();beam.moveTo(267,91);beam.lineTo(229,191);beam.lineTo(304,191);beam.close();c.drawPath(beam,p);
            }
        }
        private void drawCharacter(Canvas c){
            c.save();
            float h=108f,w=166f*h/261f,baseY=207f;
            c.translate(x-w/2f,baseY-h);
            c.scale(h/261f,h/261f);
            SpriteRig.draw(getContext(),c,action,phase,right,0f,Needs.mood(getContext())/10-5,
                Store.prefs(getContext()).getInt("kalleOutfit",0),
                Calendar.getInstance().get(Calendar.MONTH));
            c.restore();
        }
        private void drawEffects(Canvas c){
            if(effectTime<=0)return;
            float wig=(float)Math.sin(clock*3f);
            if(effect==1){
                for(int i=0;i<8;i++){
                    float xx=120+i*24, yy=72+(float)Math.sin(clock*2+i)*11;
                    p.setColor(i%2==0?0x777be2f8:0x88f4bd5e);
                    c.drawCircle(xx,yy,8+2*wig,p);
                }
                text(c,"♪  PFAND-RAVE  ♫",126,105,13,0xffffe48c);
            }else if(effect==2){
                for(int i=0;i<6;i++){
                    float xx=223+i*18+(float)Math.sin(clock+i)*7f;
                    float yy=116+(float)Math.sin(clock*2f+i)*17f;
                    p.setColor(0xffc6c4bf);c.drawOval(xx,yy,xx+18,yy+10,p);
                    p.setColor(0xfff5bd57);c.drawCircle(xx+18,yy+5,2,p);
                }
                text(c,"TAUBENMAFIA",217,100,12,0xffffe48c);
            }else if(effect==3){
                float ghostY=130f+(float)Math.sin(clock*2f)*5f;
                p.setColor(0xaaddf9ee);c.drawOval(35,ghostY,84,ghostY+62,p);
                p.setColor(0xff283543);c.drawCircle(49,ghostY+26,4,p);c.drawCircle(70,ghostY+26,4,p);
                text(c,"MIETE!",38,ghostY+46,10,0xff283543);
            }else if(effect==4){
                p.setColor(0xffafc6ab);c.drawCircle(230,184+wig*2,5,p);
                p.setColor(0xff161c18);c.drawCircle(228,183+wig*2,1.5f,p);
                c.drawCircle(232,183+wig*2,1.5f,p);
                text(c,"GEHEIM!",204,168,10,0xffffdc80);
            }else if(effect==5){
                p.setColor(0xff8edce1);c.drawOval(238,57+wig*3,308,72+wig*3,p);
                p.setColor(0xff6f7096);c.drawOval(255,46+wig*3,292,68+wig*3,p);
                text(c,"??!",269,59+wig*3,11,Color.WHITE);
            }
        }
        private void drawHud(Canvas c){
            box(c,0,0,W,42,0xea141618,0);
            text(c,"KALLE / LEBENDIGES REVIER",11,17,12,0xffffca73);
            text(c,"Eigenleben aktiv  ·  Geheimnisse "+foundCount()+"/5",11,33,9,0xffe9e8e2);
            box(c,190,6,283,34,0xff3b352e,5);
            text(c,"GEHEIMNISSE",195,24,10,0xffffe7b2);
            box(c,292,6,350,34,0xff553e37,5);
            text(c,"ZURUECK",299,24,10,Color.WHITE);
            box(c,6,211,354,238,0xe9151719,6);
            text(c,"RADIO  ·  TONNE  ·  GULLI  ·  TAUBE  ·  LAMPE",12,222,9,0xffffcb7b);
            text(c,"Tippen: Kalle laeuft hin. Nichts tun: Kalle entscheidet selbst.",12,234,8,0xfff0e9dd);
            if(bubbleTime>0&&speech!=null&&!speech.isEmpty()){
                box(c,8,48,352,98,0xe9121416,8);
                p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.2f);p.setColor(0xffd9a36c);
                c.drawRoundRect(8,48,352,98,8,8,p);p.setStyle(Paint.Style.FILL);
                String[] lines=wrap(speech,54,3);
                for(int i=0;i<lines.length;i++)text(c,lines[i],17,63+i*13,10,0xfffff4dc);
            }
        }
        private String[] wrap(String input,int width,int maxLines){
            java.util.ArrayList<String> lines=new java.util.ArrayList<>();
            StringBuilder current=new StringBuilder();
            for(String word:input.split(" ")){
                if(current.length()>0&&current.length()+word.length()+1>width){
                    lines.add(current.toString());current.setLength(0);
                    if(lines.size()==maxLines-1)break;
                }
                if(current.length()>0)current.append(' ');
                current.append(word);
            }
            if(current.length()>0)lines.add(current.toString());
            return lines.toArray(new String[0]);
        }
        private void drawJournal(Canvas c){
            box(c,11,43,349,207,0xf50d171b,10);
            text(c,"KALLES GEHEIME SAMMLUNG   "+foundCount()+"/5",24,62,13,0xffffda8c);
            for(int i=0;i<KEYS.length;i++){
                float y=82+i*24;
                boolean unlocked=found(KEYS[i]);
                text(c,(unlocked?"✓  ":"?  ")+(unlocked?SECRET_NAMES[i]:SECRET_HINTS[i]),24,y,unlocked?10:9,
                    unlocked?0xffa9e8ba:0xffd5d5ce);
            }
            text(c,"Tippe zum Schliessen. Alle Geheimnisse bleiben gespeichert.",24,199,8,0xffc5bdaf);
        }
    }
}
