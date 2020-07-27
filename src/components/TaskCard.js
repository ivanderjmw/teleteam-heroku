import React, { Component } from 'react';
import moment from 'moment';
import axios from 'axios';
import { Card, Tag, Modal, Form, Typography, Input, DatePicker, Select, Checkbox, notification } from "antd";
import { Link } from 'react-router-dom';


import {getDeadlineTagColor} from "../helpers";

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;

const TaskView = ({ visible, onCreate, onCancel, task, members, onUpdate }) => {

    const [form] = Form.useForm();

    const member_options = (members) => {
        try {
            return members.map(user => { return (<Option value={user.username}>{user.username}</Option>)});
        } catch (error) {
            return null;
        }
    }

    const assigned_users = (task) => {
        try {
            return task.assigned_users.map((user_pk) => members.find((user) => user.id === user_pk).username)
        } catch (err) {
            return 'still Loading props'
        }
    }
    

    // Below is to update the task everytime it is clicked.
    let flag = true;

    const initializeValues = (visible) => {
        if (visible === true & flag === true) {
            flag = false;
            form.setFieldsValue({
                title: task.title,
                deadline: moment(task.deadline),
                assignedUsers: assigned_users(task),
                done: task.done
            });
        } else if (visible === false & flag === false){
            flag = true;
        }
    }

    return (
        <Modal
            visible={visible}
            title={"Edit - " + task.title}
            okText="Save Changes"
            cancelText="Cancel"
            onCancel={onCancel}
            onOk={() => {
                form
                .validateFields()
                .then(values => {
                    onCreate(values);
                }).catch(error => {
                    console.log(error);
                })
            }}
            onClick={initializeValues(visible)}
            >
            <Form
                form={form}
                layout="vertical"
                name="form_in_modal"
                rules={[{ required: true, message: 'Please the task Title!' }]}
            >
                <Form.Item
                    name="title"
                    label="Title"
                >
                    <Input/>
                </Form.Item>
                <Form.Item 
                    name="deadline" 
                    className="DateTime"
                    label="Meeting time"
                    rules={[{ required: true, message: 'Please input the task deadline!' }]}
                >
                    <DatePicker 
                        showTime 
                        format="YYYY-MM-DD HH:mm"
                        allowClear={false}
                        />
                </Form.Item>
                <Form.Item 
                    name="assignedUsers" 
                    className="Assigned-Users" 
                    label="Assigned Users" 
                    rules={[{ required: true, message: 'Please input at least one assigned User!' }]}
                    >
                    <Select
                        mode="multiple"
                        style={{ width: '100%' }}
                        placeholder="Please select"
                        >
                        { member_options(members) }
                    </Select>
                </Form.Item>
                <Form.Item
                    name="done"
                    className="doneButton"
                    valuePropName="checked">
                    <Checkbox>Done</Checkbox>
                </Form.Item>
            </Form>
        </Modal>
    )
}



class TaskCard extends Component {

    constructor (props) {
        super(props);
        this.state = {
            visible: false,
            task: props.task,
            deadlineTagColor: this.props.colorCodeTag ? 
                getDeadlineTagColor(moment(this.props.task.deadline).diff(moment(), 'days')+1) :
                "#108ee9",
        };
    }

    componentDidUpdate (prevprops) {
        if (this.props.task !== prevprops.task) {
            this.setState({
                task: this.props.task,
                deadlineTagColor: this.props.colorCodeTag ? 
                    getDeadlineTagColor(moment(this.props.task.deadline).diff(moment(), 'days')+1) :
                    "#108ee9",
            });
            this.updateDeadlineTagColor();
        }
    }

    updateDeadlineTagColor = () => {
        if(this.state.task.deadline) {
            this.setState({
                deadlineTagColor: this.props.colorCodeTag ? 
                    getDeadlineTagColor(moment(this.state.task.deadline).diff(moment(), 'days')+1) :
                    "#108ee9",
            });
        }
    }


    assignedUserTags = () => {
        const assigned_users = this.state.task.assigned_users;
        try {
            return (
                assigned_users.map(user_pk => 
                    <Tag>{this.props.members.find(user => user.id === user_pk).username}</Tag>
                )
            )
        } catch (err) {
            return 'Still Loading props...'
        }
    }

    handleClick = () => {
        this.setState({visible:true});
    }

    handleCreate = async (value) => {
        let updatedTask = Object.assign({}, this.state.task, {
            title: value.title,
            deadline: value.deadline.format('DD MMMM YYYY'),
            assigned_users: value.assignedUsers.map(username => 
                this.props.members.find((user) => user.username === username).id),
            done: value.done
        });

        this.setState({
            task: updatedTask,
            visible: false,
        });

        this.updateDeadlineTagColor();

        try {
        const response = await 
            this.updateTask(value);
        } catch(err) {
            this.editErrorNotification(err);
            return
        }

        this.props.onChange();
        this.editSuccessNotification();
    }

    updateTask = async (value) => {
        return axios.post(`group/${this.state.task.group}/tasks/${this.state.task.id}/update`, {
            title: value.title,
            deadline: value.deadline.format(),
            assigned_users: value.assignedUsers.map((username)=> this.props.members.find((user) => user.username === username).id),
            done: value.done
        });
    }

    handleCancel = () => {
        this.setState({visible:false});
    }

    editSuccessNotification = () => {
        notification.success({
            message: 'Task Successfully edited!',
            duration: 2.5,
            style: {backgroundColor: '#efffcc'}
          });
    }

    editErrorNotification = (err) => {
        notification.error({
          message: `Something went wrong! ${err}`,
          duration: 4,
          style: {backgroundColor: '#ffcccb'}
        });
    };

    render () {

        return (
            <div style={{ display:"inline" }}>
            <Card 
                title={this.state.task.title} 
                style={{ width: 250, display: 'inline-block', marginLeft: 10, marginBottom: 10 }}
                hoverable={true}
                onClick={ this.handleClick }
                
                >
                <Tag color={this.state.deadlineTagColor} >
                    {moment(this.state.task.deadline).format("DD MMMM YYYY")}
                </Tag>
                <br /><br />
                {
                    !this.props.viewGroup ?
                        <span>
                        Assigned users:
                        <br />
                        {this.assignedUserTags()}
                        </span>
                    : <span>
                    <Link to={`/group?id=${this.props.task.group.id}`}>
                    <Tag color='blue'>{this.props.task.group.chat_title}</Tag>
                    </Link>
                    <br/>
                    {this.props.task.assigned_users.map(user => <Tag>{user.username}</Tag>)}
                    </span>
                    
                }
            </Card>

            {
                !this.props.viewGroup ?
                <TaskView
                visible={this.state.visible}
                onCreate={this.handleCreate}
                onCancel={this.handleCancel}
                task={this.state.task}
                members={this.props.members}
                key={this.state.task.id}
                />
                : <span/>
            }
            </div>
      );
    }
};

export default TaskCard;