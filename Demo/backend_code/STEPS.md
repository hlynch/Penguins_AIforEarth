az login
az acr create --resource-group ai4e_LYNCH_penguinguano_group --name penguinapibackend --sku Basic
az acr login --name penguinapibackend
docker tag penguinapi:test1 penguinapibackend.azurecr.io/penguinapi:test1
docker push penguinapibackend.azurecr.io/penguinapi:test1
