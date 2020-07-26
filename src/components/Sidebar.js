import React, { Component } from 'react';

import { Space, Typography, Divider } from "antd";
import MainUserDetailsBox from "./MainUserDetailsBox";
import SidebarGroup from "./SidebarGroup";

const { Title } = Typography;

class Sidebar extends Component {

    constructor() {
        super();
        this.getGroups();
    }

    getGroups = async () => {
        let user_id = localStorage.getItem('user_id')
        let res = await axios.get(`${user_id}/groups`).then(({data}) => {
            this.setState({groups: data});
        });
    }

    sidebarGroupList = (group) => {
        return <SidebarGroup name={group}/>
    }


    render () {
        if(!this.state.groups) {
            return (
                <div>
                    Loading...
                </div>
            )
        }
        return (
            <div className="sidebar">
                <Space direction="vertical">
                <MainUserDetailsBox fullName="Ivander Jonathan" username="@ivanderjmw"/>
                <Divider />
                {/* TODO: Map group state to Sidebargroups */}
                    <Title className="sidebar-submenu" level={4}>User groups</Title>
                    { this.state.groups.map(this.sidebarGroupList) }
                </Space>
                
            </div>
      );
    }
};

export default Sidebar;