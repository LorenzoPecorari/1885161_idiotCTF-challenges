from flask import  Flask, request, jsonify, abort, Response
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ctf_challenges.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.cli.command("create-db")
def create_db():
    """Creates the database."""
    with app.app_context():
        db.create_all()
    print("Database created!")

def make_json_response(data, status_code=200):
    return Response(response=json.dumps(data), status=status_code)

def success_dict(status="success", data=None):
    return  {"status": status } if data is None else  {"status": status, "data":data }

def error_dict(err_desc):
    return {"status": "error", "error_description": err_desc}

class Challenge(db.Model):
    class Category:
        allowed = ["misc", "web", "pwn", "crypto", "coding", "stego", "forensic", "rev"]
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    flag = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(255), nullable=False)
    contest_id = db.Column(db.Integer, nullable=False) #this is taken from the request (contests-ms), and it is the contest bound to the chal

    def to_dict(self):
        return {
            "type": "Challenge",
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "flag": self.flag,
            "points": self.points,
            "category": self.category,
            "contest_id": self.contest_id
        }



@app.route('/challenges', methods=["POST"])
def create_challenge():
    data = request.get_json()
    title =  data["title"]
    desc = data["description"]
    flag = data["flag"]
    points = int(data["points"])
    assert points >= 0
    category = data["category"]
    #print(category, (Challenge.Category).allowed)
    if category not in Challenge.Category.allowed:
        raise ValueError("category type not allowed")
    
    contest_id = int(data["contest_id"])
    chal_obj = Challenge(title=title, description=desc,  category=category,
                         flag=flag, points=points, contest_id=contest_id
                         )
    db.session.add(chal_obj)
    db.session.commit()
    resp_dict = success_dict("created", data={"count":1, "objects":[chal_obj.to_dict()]})
    return make_json_response(resp_dict, 201)

@app.route('/challenges', methods=["GET"])
def get_challenges():
    contest_id = request.args.get("contest_id")
    if contest_id is not None:
        contest_id = int(contest_id)
        query = Challenge.query.filter_by(contest_id=contest_id)
    else: query = Challenge.query
    results = query.all()
    l = [_.to_dict() for _ in results]
    resp_dict = success_dict(data={"count":len(l), "objects":l})
    return make_json_response(resp_dict, 200)

@app.route("/challenges/<int:challenge_id>", methods=["GET" , "PUT", "DELETE"])
def challenge_by_id(challenge_id):
    if request.method == "GET":
        result = Challenge.query.filter_by(id=challenge_id).one()
        resp_dict = success_dict(data={"count":1, "objects":[result.to_dict()]})
        return make_json_response(resp_dict, 200) 
    elif request.method == "PUT": 
        data = request.get_json()
        title =  data.get("title")
        desc = data.get("description")
        flag = data.get("flag")
        points = data.get("points")
        result = Challenge.query.filter_by(id=challenge_id).one()
        if title: result.title = title
        if desc: result.description = desc
        if flag: result.flag = flag
        if points: 
            points_casted  = int(points)
            assert points_casted >= 0
            result.points = points_casted
        db.session.commit()
        resp_dict = success_dict(data={"count":1, "objects":[result.to_dict()]})
        return make_json_response(resp_dict, 200)
    else: 
        result = Challenge.query.filter_by(id=challenge_id).one()
        db.session.delete(result)
        db.session.commit()
        return make_json_response(success_dict("deleted"), 200)

@app.route("/challenges/count_contests", methods=["GET"])
def count_contests():
    results = db.session.query(
        Challenge.contest_id, db.func.count(Challenge.id).label('challenge_count')
    ).group_by(Challenge.contest_id).all()
    
    data = [{"contest_id": r.contest_id, "challenge_count": r.challenge_count} for r in results]
    resp_dict = success_dict(data={"count": len(data), "objects": data})
    return make_json_response(resp_dict, 200)

@app.errorhandler(ValueError)
def handle_exception(error):
    response = jsonify(error_dict(str(error)))
    response.status_code = 400
    return response

@app.errorhandler(AssertionError)
def handle_exception(error):
    response = jsonify(error_dict(str(error)))
    response.status_code = 400
    return response


@app.errorhandler(sqlalchemy.exc.NoResultFound)
def handle_exception(error):
    response = jsonify(error_dict(str(error)))
    response.status_code = 404
    return response


@app.errorhandler(Exception)
def handle_exception(error):
    response = jsonify(error_dict(str(error)))
    response.status_code = 500
    return response


if __name__ == "__main__":
    app.run(debug=True, port=8081)