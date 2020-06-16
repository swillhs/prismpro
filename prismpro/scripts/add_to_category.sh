#!/bin/bash

PC_IP="$1"
PC_SSH_USER="$2"
PC_SSH_PASS="$3"
CATEGORY_TYPE="$4"
ENTITY_UUID="$5"
CATEGORY_NAME="$6"
CATEGORY_VALUE="$7"

echo "Adding category $CATEGORY_NAME with value $CATEGORY_VALUE of type $CATEGORY_TYPE"

# echo "Installing jq"
# curl -k --show-error --remote-name --location https://s3.amazonaws.com/get-ahv-images/jq-linux64.dms
# chmod u+x jq-linux64.dms
# ln -s jq-linux64.dms jq
# mv jq* ~/bin

if [ "$CATEGORY_TYPE" == "vm" ]; then
    CATEGORY_TYPE="mh_vms"
elif [ "$CATEGORY_TYPE" == "host" ]; then 
    CATEGORY_TYPE="hosts"
elif [ "$CATEGORY_TYPE" == "cluster" ]; then 
    CATEGORY_TYPE="clusters"
else
    echo "Incorrect category type" $CATEGORY_TYPE
    exit 0
fi

GET_ENDPOINT="https://${PC_IP}:9440/api/nutanix/v3/${CATEGORY_TYPE}/${ENTITY_UUID}"

output=$(curl -s -u $PC_SSH_USER:$PC_SSH_PASS -H 'Accept:application/json' -k $GET_ENDPOINT \
| jq  'del(.status)' \
| jq  --argjson catmap "{\"use_categories_mapping\": true}" '.metadata += $catmap' \
| jq  --argjson category "{\"$CATEGORY_NAME\":[\"$CATEGORY_VALUE\"]}" '.metadata.categories_mapping += ($category)' \
)

content=$(curl -X PUT -k $GET_ENDPOINT \
        --header 'Content-Type: application/json' \
        -u $PC_SSH_USER:$PC_SSH_PASS \
        --data-raw "$output" 
        )

echo "Updated successfully : $content"

exit 0

