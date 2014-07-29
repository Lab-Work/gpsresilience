error.bars<-function(x,y,stderr...) {
  ylim<-c(min(y-stderr),max(y+stderr))
  upy<-y+stderr
  downy1<-y-stderr
  arrows(x,y,x,upy,length=width,angle=90,...)
  arrows(x,y,x,downy1,length=width,angle=90,...)
 }
 

 t = read.csv("4year_features_wind/global_features.csv")
 
 
