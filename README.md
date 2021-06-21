# WhatsAppMessageAnalysis
Set of data pipelines that perform data wrangling and visualisations on imported WhatsApp messages

The script contains the following functions:
* **Import Messages** : Used to import .txt file that can be obtained from WhatsApp, the pipeline converts the .txt file into a dataframe object, and cleans it appropriately, ready for analysis.

* **basic_stats** : Function takes the clean dataframe object obtain from the *Import Messages* as an input and prints out a series of informative statistics regarding the messages.

![basic_stats_example](https://user-images.githubusercontent.com/23449348/122796707-9b850900-d2b6-11eb-8f6c-dc7fea8bd0cc.PNG)

* **total_messages_plot** : Function takes the clean dataframe object obtain from the *Import Messages* as an input and outputs a time series plot of total messages over a period of time, with the parameter *rolling_average_period* defining the time interval group (necessary for larger data sets)

![total_messages_plot_example](https://user-images.githubusercontent.com/23449348/122796770-afc90600-d2b6-11eb-9104-d7be1cb1dd75.PNG)

* **day_hour_plot** : Function takes the clean dataframe object obtain from the *Import Messages* as an input and outputs two plots, visualising cumulative plots of most common hours an days that messages were sent on.

![day_hour_plot_example](https://user-images.githubusercontent.com/23449348/122796780-b2c3f680-d2b6-11eb-8a27-12001680f0ae.PNG)

* **plot_wordcloud** : Function takes the clean dataframe object obtain from the *Import Messages* as an input and outputs a word cloud of most common words used within the messages, after stopwords have been removed. The function also allows stopwords to![Uploading total_messages_plot_example.PNG…]()
 be added or removed depending on the vocabulary used, the total number of words displayed can be changed using the *nwords* parameters.

![plot_wordcloud_example](https://user-images.githubusercontent.com/23449348/122796817-bc4d5e80-d2b6-11eb-82b2-68ca53c9221a.PNG)
