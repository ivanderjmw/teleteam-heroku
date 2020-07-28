import React from 'react';
import { Typography, Space, Row, Col, Tabs , Divider, Progress, List, Card, Avatar, TimePicker } from 'antd';
import { TaskCardList, MemberCardList, MeetingCardList, CreateTaskButton, CreateMeetingButton, TasksStatistics }from '../components';
import axios from 'axios';
import moment from 'moment';

import './GroupPage.css';

const { Title, Paragraph, Text } = Typography;
const { TabPane } = Tabs;

const { Meta } = Card;

class GroupPage extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            group: this.props.group,
            str: 'This is an editable text. You can set your Goal here.',
            tasks: null,
          };
        this.getGroupDetail();

        this.appendTask.bind(this);
        this.appendMeeting.bind(this);
        this.reloadTask.bind(this);
    }
    
    componentDidUpdate(prevProps, prevState) {
        if (prevProps !== this.props) {
            this.getGroupDetail();
          }
    }
    
    onChange = str => {
        this.setState({ str });
    };

    getGroupDetail = async () => {
        let group_id = this.props.group.id;
        console.log(`group id is ${group_id}`);
        return axios.get(`group/${group_id}`).then( ({data}) => {
            this.setState({
                group_data: data,
            });
        })
    }

    appendTask = (newtask) => {
        let temp = this.state.group_data;
        console.log(temp);
        temp.tasks.push(newtask);
        this.setState({group_data: temp});
    }

    appendMeeting = (newmeeting) => {
        let temp = this.state.group_data;
        console.log(temp);
        temp.meetings.push(newmeeting);
        this.setState({group_data: temp});
    }

    reloadTask = () => {
        this.getGroupDetail();
    }

    render() {
        if (!this.state.group_data) {
            return (
            <div>
                Loading...
            </div>
            );
        }
        return (
        <div className="Page">
            <Row align="middle" className="group-header">
            <Col span={12}>
                <Title>{this.state.group_data.chat_title}</Title>
                <Text>This is a Group Page. Scroll down to view members, tasks, meetings, and statistics!</Text>
            </Col>
            <Col span={12} style={{ textAlign:"right" }}>
                <Space>
                    <CreateTaskButton
                        members={this.state.group_data.members}
                        group_id={this.state.group_data.id}
                        onCreateTaskUpdate={this.appendTask}
                    />
                    <CreateMeetingButton
                        members={this.state.group_data.members}
                        group_id={this.state.group_data.id}
                        onCreateMeetingUpdate={this.appendMeeting}
                    />
                </Space>
            </Col>
            </Row>

            <Divider/>

            <Title level={2}>Members</Title>
            <Text>List of members that are in your group. Ask them to enter <span className='highlight'>/join</span> command in your telegram group if they don't show up here.</Text>
            <br/>
            <MemberCardList members={this.state.group_data.members}/>

            <Divider/>

            <Title level={2}>Tasks</Title>
            <Text>Your tasks are listed here in sorted date. Click on a task to edit it! You can create a task by clicking the create task button, or enter the <span className='highlight'>/createtask</span> command in your telegram group.</Text>
            <Tabs defaultActiveKey="1"
            tabBarExtraContent={
                <CreateTaskButton
                        members={this.state.group_data.members}
                        group_id={this.state.group_data.id}
                        onCreateTaskUpdate={this.appendTask}
                    />
            }>
                <TabPane tab="My Tasks" key="1">
                    <TaskCardList 
                        colorCodeTags={true} 
                        members={this.state.group_data.members} 
                        tasks={this.state.group_data.tasks.filter((task) => !task.done)} 
                        onChange={this.getGroupDetail}
                        key={1}
                        />
                </TabPane>
                <TabPane tab="Completed" key="2">
                    <TaskCardList 
                        colorCodeTags={false} 
                        members={this.state.group_data.members}
                        tasks={this.state.group_data.tasks.filter((task) => task.done)} 
                        onChange={this.reloadTask}
                        key={2}
                        />
                </TabPane>
            </Tabs>

            <Divider/>

            <Title level={2}>Meetings</Title>
            <Text>Upcoming meetings are listed here. Click the tab pane to look at past meetings. You can enter <span className='highlight'>/createmeeting</span> command in Telegram to create a meeting, or click the button. In telegram you can add make a poll by sending <span className='highlight'>/createpoll</span> to the Teleteam bot in private chat.</Text>
            <Tabs defaultActiveKey="1" 
                    tabBarExtraContent={<CreateMeetingButton
                        members={this.state.group_data.members}
                        group_id={this.state.group_data.id}
                        onCreateMeetingUpdate={this.appendMeeting}
                    />}
                    >
                <TabPane tab="Upcoming" key="1">
                    <MeetingCardList 
                        meetings={this.state.group_data.meetings.filter((meeting) => meeting.time > moment().format())} 
                        onChange={this.getGroupDetail}
                        colorCodeTags={true}
                        />
                </TabPane>
                <TabPane tab="Past" key="2">
                    <MeetingCardList 
                        meetings={this.state.group_data.meetings.filter((meeting) => meeting.time < moment().format())} 
                        onChange={this.getGroupDetail}
                        colorCodeTags={false}
                        />
                </TabPane>
            </Tabs>

            <Divider/>

            <TasksStatistics tasks={this.state.group_data.tasks} />

        </div>
    )
    }
}

export default GroupPage;