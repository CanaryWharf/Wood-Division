cd ./DDragon
wget http://ddragon.leagueoflegends.com/cdn/dragontail-$1.tgz
mkdir $1
tar -xzvf dragontail-$1.tgz -C $1

for dir in *
do
    if [ "$dir" != $1 ]
    then
        rm -rf $dir
    fi
done
