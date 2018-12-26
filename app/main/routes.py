from flask import  render_template ,Blueprint
main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
	user = {'username':'Miguel'}
	posts = [ ]
 #        {
 #            'author': {'username': 'John'},
 #            'body': 'Beautiful day in Portland!'
 #        },
 #        {
 #            'author': {'username': 'Susan'},
 #            'body': 'The Avengers movie was so cool!'
 #        }
 #    ]
    # posts=[]
	return render_template('index.html', title='Home', posts=posts)

