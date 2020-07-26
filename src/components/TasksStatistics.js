import React from 'react';
import moment from 'moment';

import {Row, Col, Typography, Progress, Tag} from 'antd';

const { Title, Paragraph, Text } = Typography;

class TasksStatistics extends React.Component{
    
    getPercentOverdue = tasks => {
        const numOverdueTasks = tasks.filter((task) => {
            return(task.deadline && moment(task.deadline) < moment() && !task.done);
        }).length;
        
        return (numOverdueTasks / tasks.length) * 100;
    };

    getPercentDone = tasks => {
        const numDoneTasks = tasks.filter((task) => task.done).length;

        return (numDoneTasks / tasks.length) * 100;
    };

    render(){

        if (this.props.tasks.length == 0){
            return (
                <span>Create tasks to see the statistics</span>
            );
        }

        // An array of tasks with deadline within a week ago and a week from 
        // now.
        let tasksWithNearDeadlines = this.props.tasks.filter(task => {
            return (moment(task.deadline) > moment().subtract(8, 'days') 
            && 
            moment(task.deadline) < moment().add(8, 'days'))
        });

        const percentOverdue = Math.round(this.getPercentOverdue(tasksWithNearDeadlines));
        const percentDone = Math.round(this.getPercentDone(tasksWithNearDeadlines));
        const percentUpcoming = 100 - percentOverdue - percentDone;

        return (
            <div>
            <Title level={2}>Statistics</Title>
            <Row gutter={[32,8]}>
                <Col span={14}>
                <Title level={4}>Tasks due between a week ago and a week from now</Title>
                
                {/* The Progress component can only support two values 
                (percent and successPercent), so the overdue tasks take up
                is represented red background, giving the illusion that there are 
                three parts to the Progress line. */}
                <Progress 
                    percent={percentUpcoming} 
                    successPercent={percentDone} 
                    showInfo={false}
                    trailColor="red"/>
                
                <Tag color="#87d068" style={{marginBottom:"5px"}}>
                    Done: {percentDone}%
                </Tag>
                <br />

                <Tag color="#108ee9" style={{marginBottom:"5px"}}>
                    Upcoming: {percentUpcoming}%
                </Tag>
                <br />

                <Tag color="#f50" style={{marginBottom:"5px"}}>
                    Overdue: {percentOverdue}%
                </Tag>
                
                </Col>
                {/* TODO: Create the all time stats (?) */}
                {/* <Col span={12}>
                    <Title level={4}>All time stats</Title>
                    
                    <Progress percent={60} successPercent={45}/>
                    
                    <div style={{ height: '16px' }}/>
                    <Text strong={true}>Summary:</Text>
                </Col> */}
            </Row>
            </div>
        );
    }
}

export default TasksStatistics;
