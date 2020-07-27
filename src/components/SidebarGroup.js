import React, { Component } from 'react';
import moment from 'moment';

import { Avatar, Tag } from "antd";

import {getDeadlineTagColor} from "../helpers";

class SidebarGroup extends Component {
    constructor(props) {
        super(props);
        this.state = {group: props.group};
    }

    componentDidUpdate(prevProps) {
        if (prevProps.group !== this.props.group) {
          this.setState({group: this.props.group});
        }
    }

    // Automatically find the closest deadline of the tasks in the group, and 
    // return a "... days" tag
    getClosestDeadlineTag = () => {
        let min = moment(this.state.group.closest_deadline);

        const daysToClosestDeadline = min.diff(moment(), 'days')+1;
        const tagColor = getDeadlineTagColor(daysToClosestDeadline);

        return (
        <Tag color={tagColor} 
                style={{float: 'right', marginTop: '10px'}}>
                {daysToClosestDeadline} day{daysToClosestDeadline>1 ? 's' : ''}
        </Tag>);
    }

    render () {
        return (
        <div className="sidebar-group">
            <Avatar className="sidebar-group-dp" src={this.props.group.photo_url ? this.props.group.photo_url: "https://wwwmpa.mpa-garching.mpg.de/galform/cr/CR_LCDM_dump30_400_170000_12000_100_blue.gif"}/> 
            <h3 className="sidebar-group-name">{this.props.group.chat_title}</h3> 
            {this.getClosestDeadlineTag()}
        </div>  
      );
    }
};

export default SidebarGroup;