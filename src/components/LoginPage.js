import React, {Component} from 'react';

class LoginPage extends Component {
	constructor(props) {
		super(props);

		this.state = {
			username: '',
			password: '',
		};

		this.handleSubmit = this.handleSubmit.bind(this);
	}


	handleSubmit(event) {
		event.preventDefault();
		const loginData = {
			username: this.state.username,
			password: this.state.password,
		};
		if (loginData.username === '' || loginData.password === '') {
			console.log('need all fields');
			return;
		}
		// post API call to backend for login auth
		fetch('http://localhost:5000/auth/login', {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(loginData)
		}).then((res) => {
			console.log(res);
			if (res.ok) {
				res.json().then(data => ({
					data: data,
					status: res.status
				})).then(res => {
					console.log(res);
					const userID = res.data.userID;
					console.log(userID);
					window.location = '/home/' + userID; // direct to homepage based on userID
				});
			} else {
				console.log('error while fetching');
			}
		});
		event.preventDefault();
	}

	render() {
		return (
			<div className="row">
				<div className="col-4"></div>
				<form className="form-signin col-4" onSubmit={this.handleSubmit}>       
					<h2 className="form-signin-heading">Please login</h2>
					<input 
						type="text" 
						className="form-control" 
						name="username" 
						placeholder="Username" 
						required="" 
						autofocus=""
						onChange={(e) => { this.setState({ username: e.target.value})}}
					/>
					<input 
						type="password" 
						className="form-control" 
						name="password" 
						placeholder="Password" 
						required=""
						onChange={(e) => { this.setState({ password: e.target.value})}}
					/>      
					<button 
						className="btn btn-lg btn-primary btn-block" 
						type="submit"
					>
						Login
					</button>   
				</form>
				<div className="col-4"></div>
			</div>
		);
	}
}

export default LoginPage;