fastq_fs () {
        READ_NAME_LEN=`head -1 $1 | wc -c`
        READ_LEN=`head -2 $1 | tail -1 | wc -c`
        FILE_SIZE=`ls -l $1 | awk '{print $5}'`
        expr $FILE_SIZE \* $READ_LEN \/ \($READ_NAME_LEN + \($READ_LEN \* 2 \) + 2 \)
}
