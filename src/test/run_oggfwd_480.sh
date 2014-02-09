echo "Feeding http://localhost:4551:/480.ogg forever ..."
while true
do
  oggfwd localhost 4551 1qaz /480.ogg < /root/Downloads/big_buck_bunny_480p_stereo.ogg
done

