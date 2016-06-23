## django-config-storage

[![Build Status](https://travis-ci.org/princeofdatamining/django-config-storage.png?branch=master)](https://travis-ci.org/princeofdatamining/django-config-storage)

`django-config-storage` is a Django appliation and library:  configuration for each applications.

## Setup

Install by downloading the source and running:

> pip install https://bitbucket.org/princeofdatamining/prodm-django-configuration/get/master.zip

and then add it to your installed apps:

    INSTALLED_APPS = (
        ...
        'config_storage',
        ...
    )

and then run `migrate`:

> python manage.py migrate

## Usage

Create a configuration model in your `models.py`:

	from config_storage.models import Configuration
	
	class ProjConfig(Configuration):
	
		class Meta:
			# dont remove this line
			abstract = True
			verbose_name = 'Project Config'
			
		str_val = models.CharField(max_length=100)
		int_val = models.IntegerField()
		
Use this configuration:

	conf = ProjConfig()
	# get value
	print(conf.str_val, conf.int_val)
	# change value
	conf.int_val = 100
	# save
	conf.save()
