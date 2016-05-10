var ReactDOM = require('react-dom')
var React = require('react')
var App = require('./app.jsx')
var Csrf = require('./csrf.jsx')

var LoginForm = React.createClass({
  componentDidMount: function() {
    $('.register').click(function() {
      ReactDOM.render(
        <RegistrationComponent url1="/api/user/" url2="/api/workbench-user/" />,
        document.getElementById('react-app')
      )
    });
  },
  getInitialState: function() {
    return {username: '', password: ''}
  },
  handleUsernameChange: function(e) {
    this.setState({username: e.target.value})
  },
  handlePasswordChange: function(e) {
    this.setState({password: e.target.value})
  },
  handleSubmit: function(e) {
    e.preventDefault();
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      type: 'POST',
      data: {'username': this.state.username, 'password': this.state.password, csrfmiddlewaretoken: Csrf},
      success: function(data) {
        // unload current component
        console.log(data)
        // move on to main Experiment page
        this.setState({username: '', password: ''})
      }.bind(this),
      error: function(xhr, status, error) {
        console.log(this.props.url, status, error.toString());
      }.bind(this),
    });
  },
  render: function() {
    return (
      <form onSubmit={this.handleSubmit}>
        <h3>Sign in to continue</h3>
        <a href="#" className="register">Create an account</a>
        <div className="form-group">
          <label>Username:</label>
          <input
            type="text"
            placeholder="Username"
            value={this.state.username}
            onChange={this.handleUsernameChange}
            className="form-control"
            />
          </div>
          <div className="form-group">
            <label>Password:</label>
            <input
              type="password"
              placeholder="Password"
              value={this.state.password}
              onChange={this.handlePasswordChange}
              className="form-control"
              />
          </div>
          <input type="submit" value="Sign in" className="form-control btn btn-success" />
        </form>
    )
  }
});

var RegistrationComponent = React.createClass({
  getInitialState: function() {
    return ({username: '', emailaddress: '', password_original: '', password_again: ''})
  },
  handlePasswordChange: function(e) {
    this.setState({password_original: e.target.value})
  },
  handlePasswordCopyChange: function(e) {
    this.setState({password_again: e.target.value})
    if (this.state.password_original.trim() == e.target.value.trim()) {
      $('.password-glypicon').addClass('glyphicon-ok')
    }
  },
  handleSubmit: function(e) {
    $.ajax({
      type: 'POST',
      dataType: 'json',
      url: this.props.url1,
      data: {username: this.state.username, password: this.state.password, emailaddress: this.state.emailadress, csrfmiddlewaretoken: Csrf},
      success: function(data) {
        console.log('data')
      }.bind(this),
      error: function(xhr, status, err) {
        console.log(this.props.url1, status, err.toString())
      }.bind(this)
    });
  },
  handleUsernameChange: function(e) {
    this.setState({username: e.target.value})
  },
  handleEmailChange: function(e) {
    this.setState({emailaddress: e.target.value})
  },
  render: function() {
    return (
      <form onSubmit={this.handleSubmit}>
        <h3>Create an account</h3>
        <div className="form-group">
          <label>Username:</label>
          <input
            type="text"
            placeholder="Username"
            value={this.state.username}
            onChange={this.handleUsernameChange}
            className="form-control"
            required
            />
        </div>
        <div className="form-group">
          <label>Email address:</label>
          <input
            type="text"
            placeholder="Email address"
            value={this.state.emailaddress}
            onChange={this.handleEmailChange}
            className="form-control"
            required
            />
        </div>
        <div className="form-group">
          <label>Password:</label>
          <input
            type="password"
            placeholder="Password"
            value={this.state.password_original}
            onChange={this.handlePasswordChange}
            className="form-control password"
            required
            />
        </div>
        <div className="form-group">
            <label>Password (again):</label>
            <input
              type="password"
              placeholder="Password (again)"
              value={this.state.password_again}
              onChange={this.handlePasswordCopyChange}
              className="form-control password"
              required
              />
              <i className="glyphicon password-glypicon" />
        </div>
        <input type="submit" value="Register" className="btn btn-success" />
      </form>
    )
  }
})
ReactDOM.render(<LoginForm url="/sign-in/" />,
  document.getElementById('react-app')
);
