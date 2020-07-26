import React, { Component } from 'react';
import MemberCard from "./MemberCard";
import axios from 'axios';


class MemberCardList extends Component {
    // constructor(props) {
    //     super(props);
    // }

    state = {
        members: this.props.members
    }

    componentDidUpdate(prevProps, prevState) {
        if (prevProps !== this.props) {
            this.updateState();
          }
    }
    
    componentDidMount() {
        this.updateState();
    }

    updateState () {
        this.setState({
            members: this.props.members
        });
    }

    render () {
        const MemberCards = () => {
            return this.state.members.map((user) =>
            <MemberCard user={user} />);
        }

        if (!this.state.members) {
            return 'Loading...'
        }
        return (
            <div>{MemberCards()}</div>
        );
    }
}

export default MemberCardList;