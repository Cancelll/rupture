HTMLDIR="$HOME/.rupture/client/client_1"

i=1

# URL_IP=$(sed -n ${i+10}p ip-domain.csv)

# echo $URL_IP

# ./rupture --attack &

# firefox $HTMLDIR/test.html &
echo "web:
    endpoint: 'https://"$URL"?%s'
    prefix: 'imper'
    alphabet: 'abcdefghijklmnopqrstuvwxyz'
    secretlength: 8
    alignmentalphabet: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    recordscardinality: 1
    method: 'serial'
    samplesize: 1
    confidence_threshold: 1.0" >> backend/target_config.yml