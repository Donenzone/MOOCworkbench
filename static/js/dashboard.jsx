var React = require('react')

module.exports = React.createClass({
   render: function(){
     var username = this.props.username;
       return (
         <div id="main">
          <h1>MOOC Workbench</h1>
          <p>Welcome, {username}</p>
          <ExperimentWizard />
         </div>
       )
   }
});

var ExperimentWizard = React.createClass({
  getInitialState: function() {
    return {'title': ''}
  },
  handleTitleChange: function(e) {
    this.setState({title: e.target.value})
  },
  render: function() {
    return (
      <form>
        <h3>Create a new experiment</h3>
        <TitleComponent
          value={this.state.title}
          onChange={this.handleTitleChange}
          />
        <TextAreaComponent
          label="Description"
          type="text"
          placeholder="Description of the experiment you wish to work on..."
          required="required"
          value={this.state.description}
          onChange={this.handleDescriptionChange}
          />
          <SubmitButtonComponent value="Submit" type='success' />
      </form>
    )
  }
})

var TitleComponent = React.createClass({
  render: function() {
    return (
      <InputComponent
        label="Title"
        type="text"
        placeholder="Enter a title..."
        required="required"
        />
    )
  }
})

var InputComponent = React.createClass({
  render: function() {
    return (
      <div className="form-group">
        <label>{this.props.label}:</label>
        <input
          type={this.props.type}
          placeholder={this.props.placeholder}
          className="form-control"
          required={this.props.required}
          />
      </div>
    )
  }
})

var SubmitButtonComponent = React.createClass({
  render: function() {
    var classes = 'form-control btn btn-' + this.props.type
    return (
      <input type="submit" value={this.props.value} className={classes} />
    )
  }
})

var TextAreaComponent = React.createClass({
  render: function() {
    return (
      <div className="form-group">
        <label>{this.props.label}:</label>
        <textarea
          placeholder={this.props.placeholder}
          className="form-control"
          required={this.props.required}
          rows="5"
          />
      </div>
    )
  }
})
