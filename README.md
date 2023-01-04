<h1 align="center"> Youtube Channel Videos Analysis </h1>

---
⭐ Star it on GitHub!
## Description

Nowadays, almost everyone is using **Youtube**. And there is a project to get an analysis of videos from a particular channel. For example best/worst performing videos, view distribution per video, view duration, etc...

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install
* from **googleapiclient.discovery** import **built**
* from **IPython.display** import **JSON**
* from **dateutil.parser** import **parse**

You will also need **pandas**, **matplotlib**, and **seaborn**.

After finishing the installations, clone the repository:
```bash
git clone https://github.com/Karazakoff/youtube-api-analysis.git
```

## Usage

_We recommend you run a **Jupyter** file instead of a **Python** file because of better visualization, but you are free to choose any of these files._

You must provide the **channel id** from the desired channel on [Youtube](https://www.youtube.com/), and do not forget to add to the list which is shown below (channel_ids - python list).

```python
api_service_name = "youtube"
api_version = "v3"

channel_ids = ['UCKP6ezsWMNsovDGRJY0sAbQ',
               # more channels here
]

# Get credentials and create an API client
youtube = build(api_service_name, api_version, developerKey = api_key)
```
In this example, we are using [Ali Abdaal's](https://www.youtube.com/@aliabdaal) channel. But you can choose any channel you want.

And that's it, after executing you will receive nice graphs!


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
