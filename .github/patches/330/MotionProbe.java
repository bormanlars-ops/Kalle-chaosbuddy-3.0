package de.boyka.kallebuddy;
public final class MotionProbe {
 public static void main(String[]args) {
   float x=175f, target=287f;
   for(int i=0;i<400;i++){
     float previous=x;
     x=RevierMotion.step(x,target,48f,1f/30f);
     if(x<previous||x>target||x-previous>2.41f)throw new AssertionError("forward teleport at "+i);
   }
   if(!RevierMotion.arrived(x,target))throw new AssertionError("never arrived on right");
   target=114f;
   for(int i=0;i<500;i++){
     float previous=x;
     x=RevierMotion.step(x,target,48f,1f/30f);
     if(x>previous||x<target||previous-x>2.41f)throw new AssertionError("backward teleport at "+i);
   }
   if(!RevierMotion.arrived(x,target))throw new AssertionError("never arrived on left");
   if(RevierMotion.step(40f,150f,48f,100f)>42.41f)throw new AssertionError("uncapped frame delta");
   if(RevierMotion.step(100f,180f,40f,-1f)!=100f)throw new AssertionError("negative delta");
   System.out.println("PASS: no teleport, continuous back-and-forth and frame-time capped");
 }
}
