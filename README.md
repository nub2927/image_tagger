# image_tagger
python script to help streamline the tagging process
two files of concern:
withdeepbooru.py uses the DeepBooru model 
https://github.com/KichangKim/DeepDanbooru
download one of the pretrained releases at https://github.com/KichangKim/DeepDanbooru/releases/
and unzip in the models folder 

configurations:
in config you can entrer default_tags which are tags that will be automatically added to each images
and quick acess tags which in withoutdeepbooru will create a quick acess penal with those tags

deep_booru_threshold controls how much confidence a tag has to have before being display 
