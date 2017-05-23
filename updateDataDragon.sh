cd ./static/DDragon
if mkdir updateLock;
then
    wget http://ddragon.leagueoflegends.com/cdn/dragontail-$1.tgz
    mkdir -p $1
    tar -xzvf dragontail-$1.tgz -C $1
    sleep 1

    for dir in *
    do
        if [ "$dir" != $1 ]
        then
            rm -rf $dir
        fi
    done
else
    exit 1
fi
