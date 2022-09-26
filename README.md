# image_tagger
python script to help streamline the tagging process

process is you open a folder with images in them
if there are txt files with the same name as the image in the same directory it will parse the tags from there.
you press the buttons under current tags to toggle whether you want the tags to be saved in the final text file or not. you can also search for tags to add under tag search. when finished all the tags are saved simultanously. if there are txt files in the directory with the same name as the images they will be overwritten and neew text file with the information from the application will be saved in place.  changes are only saved when save all is pressed
the "a" and "d" keys are used to move through the pictures in the folder


two files of concern:
withdeepbooru.py uses the DeepBooru model 
https://github.com/KichangKim/DeepDanbooru
download one of the pretrained releases at https://github.com/KichangKim/DeepDanbooru/releases/
and unzip in the models folder 

configurations:
in config you can entrer default_tags which are tags that will be automatically added to each images
and quick acess tags which in withoutdeepbooru will create a quick acess penal with those tags

deep_booru_threshold controls how much confidence a tag has to have before being display 
