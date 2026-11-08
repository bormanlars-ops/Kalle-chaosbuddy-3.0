package de.boyka.kallebuddy;

/** Device-independent, continuous motion with a capped frame step. */
final class RevierMotion {
    private RevierMotion(){}
    static float step(float x,float target,float unitsPerSecond,float seconds){
        float dt=Math.max(0f,Math.min(.05f,seconds));
        float amount=Math.max(0f,unitsPerSecond)*dt;
        float difference=target-x;
        if(Math.abs(difference)<=amount)return target;
        return x+Math.signum(difference)*amount;
    }
    static boolean arrived(float x,float target){return Math.abs(x-target)<.3f;}
}
