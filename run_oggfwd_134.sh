echo "Feeding http://localhost:4551:/134.ogg forever ..."

while true
do
    oggfwd localhost 4551 1qaz /134.ogg < ~/Downloads/Big_Buck_Bunny_small.ogv
done

