import React, { Component } from 'react';
import { Card, Avatar } from 'antd';

const { Meta } = Card;

class MemberCard extends Component {

    constructor (props) {
        super(props);
        this.state = {
          visible: false,
          user: null,
        };
    }

    handleClick = () => {
        this.setState({visible:true});
    }

    handleCreate = (value) => {
        console.log(value, this.props.task.title)
        this.setState({visible:false});
    }

    handleCancel = () => {
        this.setState({visible:false});
    }

    render () {
        return (
            <div style={{ display:"inline" }}>
            <Card 
                style={{ width: 250, display: 'inline-block', marginLeft: 10, marginBottom: 10, alignContent: 'middle' }}
                hoverable={true}
                onClick={ this.handleClick }
                >
                    <Meta
                    avatar={
                    <Avatar src={this.props.user.photo_url} />
                    }
                    title={this.props.user.username}
                    />
            </Card>
            </div>
      );
    }
};

export default MemberCard;