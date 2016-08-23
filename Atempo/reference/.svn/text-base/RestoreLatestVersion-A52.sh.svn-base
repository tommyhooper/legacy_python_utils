#!/bin/sh
#########################################################
#               Author: Jerry Graczyk                   #
#               Sr. Architect, Atempo                   #
#               Date: Sept 2011                         #
#                                                       #
#    This script will list search the catalog in an     #
#    Application folder. Then create a new script       #
#    (for each directory), Restore the latest version   #
#    of files in that directory. Also create a file     #
#    containing the list of restored files.             #
#                                                       #
#########################################################
# Modify with the proper path for tina below
SOURCE=/usr/Atempo/tina/.tina.sh
 source $SOURCE
#
# Modify with the application name where resoted files reside
APPLICATION=tina.a52.com.fs
#
# Modify with the TiNa prividge user and password
# ie. root:RUKR@ZY or if no passwd root:
IDENTITY=root:@52rp3l
#
# Modify the path of where you want to keep your files 
#  for the scripts and rsports
SRPATH=/data/tina_reports
#
# Modify with the path of where you want to put temporary working files 
TWPATH=/data/tina_reports/work
#
CURDATETIME=`date +%m-%d-%Y-%H-%M-%S`
CURDATE=`date +%m-%d-%Y`
#
#  Get top folder level
clear
echo  Time Navigator - Restore Last File Version Script
echo                Starting
echo
echo
echo
echo
echo  "Enter the Root Directory! ie. /2011 Archives"
read ROOTDIR
#
# Create temporary working files
FILE1=$TWPATH/1-$CURDATE.txt
#
if [ -f $FILE1 ];
	then
        rm $FILE1
    else
         echo
	 #   echo  "$FILE1 created"
fi
#
FILE2=$TWPATH/2-$CURDATE.txt
#
if [ -f $FILE2 ];
	then
        rm $FILE2
    else
         echo
	  #  echo  "$FILE2 created"
fi
#
FILE3=$TWPATH/3-$CURDATE.txt
#
if [ -f $FILE3 ];
	then
        rm $FILE3
    else
         echo
	  #  echo  "$FILE3 created"
fi
#
FILE4=$TWPATH/4-$CURDATE.txt
#
if [ -f $FILE4 ];
	then
        rm $FILE4
    else
         echo
	  #  echo  "$FILE4 created"
fi
#
DIRECTORY=$TWPATH/DIRECTORY-$CURDATE.txt
#
if [ -f $DIRECTORY ];
	then
        rm $DIRECTORY
    else
         echo
	 #   echo  "$DIRECTORY created"
fi
#
PROJECT=$TWPATH/PROJECT-$CURDATE.txt
#
if [ -f $PROJECT ];
	then
        rm $PROJECT
    else
        echo
	  #  echo  "$PROJECT created"
fi
#
TEMP=$TWPATH/TEMP-$CURDATE.txt
#
if [ -f $TEMP ];
	then
        rm $TEMP
    else
         echo
	  #  echo  "$TEMP created"
fi
#
TEMP1=$TWPATH/TEMP1-$CURDATE.txt
#
if [ -f $TEMP1 ];
	then
        rm $TEMP1
    else
         echo
	  #  echo  "$TEMP1 created"
fi
# Search catalog in Application folder for backed up files
#      tina_find -path_folder /   -application $APPLICATION -catalog_only -long -lost_files -depth 10Y -identity $IDENTITY -display_cart > $FILE1
       tina_find -path_folder /   -application $APPLICATION -catalog_only -long -depth 10Y -identity $IDENTITY -display_cart > $FILE1
# grab directoroes from the list      
      cat $FILE1 | grep "$ROOTDIR" |grep "dir  "> $FILE2
# grab the path of the directories      
      cat $FILE2 | tr -s ' ' | cut   -d ' ' -f 15- >> $DIRECTORY
# grab the subdirectory of the path      
      cat $DIRECTORY | cut -d '/' -f 3 >>$PROJECT
      awk ' !x[$0]++' $PROJECT > $TEMP
      sed '/^$/d' $TEMP > $PROJECT
      echo
# create restore script(s) and report files      
cat $PROJECT | while read D
  do
       RESTOREDFILES=$SRPATH/Restored_files_for_$D-$CURDATETIME.txt
        if [ -f $RESTOREDFILES ];
       then
         rm $RESTOREDFILES
       else
         echo "$RESTOREDFILES created"
      fi
       SCRIPTA=$SRPATH/$D-$CURDATETIME.sh
      if [ -f $SCRIPTA ];
       then
         rm $SCRIPTA
       else
         echo "$SCRIPTA created"
      fi
#
        echo '#!/bin/sh' >$SCRIPTA
        echo "source $SOURCE" >>$SCRIPTA
        echo 'ARGS=1' >>$SCRIPTA 
        echo 'RESTOREPATH=$1' >>$SCRIPTA
        echo 'if [ $# -ne $ARGS ] ; then' >>$SCRIPTA
        echo '	echo "You must enter the Restore Path Directory! ie. /project1/restore"' >>$SCRIPTA
        echo '	exit 65' >>$SCRIPTA
        echo 'else ' >>$SCRIPTA
        echo 'echo' >>$SCRIPTA
        echo 'fi' >>$SCRIPTA
        chmod 755 $SCRIPTA
  #     echo "tina_restore -path_folder "'"'$ROOTDIR/$D'"'" -folder appl.$APPLICATION -path_dest "'$RESTOREPATH'" -depth 10Y"  >>$SCRIPTA
        echo "tina_restore -path_folder "'"'$ROOTDIR/$D'"'" -folder appl.$APPLICATION -path_dest "'$RESTOREPATH'" -depth 10Y -test_mode standard"  >>$SCRIPTA
        cat $FILE1 | grep "$ROOTDIR/$D" |grep "file " > $RESTOREDFILES
        cat $RESTOREDFILES | cut -d '[' -f 2 |cut -d ']' -f 1 | cut -d ',' -f 1 > $FILE3
        cat $RESTOREDFILES | cut -d '[' -f 2 |cut -d ']' -f 1 | cut -d ',' -f 2 > $FILE3
        cat $RESTOREDFILES | cut -d '[' -f 2 |cut -d ']' -f 1 | cut -d ',' -f 3 > $FILE3
        cat $RESTOREDFILES | cut -d '[' -f 2 |cut -d ']' -f 1 | cut -d ',' -f 4 > $FILE3
        awk ' !x[$0]++' $FILE3 >> $FILE4
        sed '/^$/d' $FILE4 > $FILE3
   cat $FILE3 | while read C
      do
        tina_cart_control -label $C -status >> $TEMP1
      done 
       cat $TEMP1 >> $RESTOREDFILES
 done  
 echo
 echo
 echo   !!!!!!!!!!!  Script is completed  !!!!!!!!!!!
# Cleanup 
exit 0
