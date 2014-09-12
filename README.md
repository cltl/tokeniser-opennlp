tokeniser-opennlp
=================

Tokenizer and sentence splitter based on opennlp

You will need to have opennlp installed on your machine and
set some variables in the script `tokeniser_opennlp.py`. These two lines have
to be changed to the path where open-nlp is installed and where the models
have been store.

```shell
######### VARS ######
opennlp_folder = '/home/ruben/apache-opennlp-1.5.2-incubating'
model_folder = os.path.join(opennlp_folder,'models')
################
```

The pre-trained models can be found at http://opennlp.sourceforge.net/models-1.5/.
The script is using the default name of the models, but in case you use another
names for the models, you will need to change also the lines of code that look like:
```shell
token_model_nl = os.path.join(model_folder,'nl-token.bin')
```

There are two parameters for the script, the language (-l or --lang) and if you want
to use a wildcard for the timestamp in the header (--no-time). An example for calling
the script would be:
```shell
echo 'This is an English text' | python tokeniser_opennlp.py -l en > my_out.kaf
```

Contact
------

* Ruben Izquierdo Bevia
* ruben.izquierdobevia@vu.nl
* Vrije University of Amsterdam