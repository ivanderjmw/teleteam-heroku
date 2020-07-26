import React, { Component } from 'react';
import axios from 'axios';
import moment from 'moment';

import { Card, Tag, Modal, Form, Typography, Input, DatePicker, Select, notification } from "antd";

import getDeadlineTagColor from "../helpers";

const { Option } = Select;

const MeetingView = ({ visible, onCreate, onCancel, meeting }) => {

    const [form] = Form.useForm();

    return (
        <Modal
            visible={visible}
            title={"Edit - " + meeting.title}
            okText="Save Changes"
            cancelText="Cancel"
            onCancel={onCancel}
            onOk={() => {
                form
                .validateFields()
                .then(values => {
                    onCreate(values);
                })
            }}
            >
            <Form
                form={form}
                layout="vertical"
                name="form_in_modal"
                initialValues={{
                    modifier: 'public',
                    title: meeting.title,
                    time: moment(meeting.time)
                }}
            >
                <Form.Item
                    name="title"
                    label="Title"
                >
                    <Input defaultValue={meeting.title}/>
                </Form.Item>
                <Form.Item 
                    name="time" 
                    className="DateTime"
                    label="Meeting time"
                >
                    <DatePicker 
                        showTime 
                        format="YYYY-MM-DD HH:mm" 
                        allowClear={false}
                        />
                </Form.Item>
            </Form>
        </Modal>
    )
}



class MeetingCard extends Component {

    constructor (props) {
        super(props);
        this.state = {
          visible: false,
          meeting: this.props.meeting,
          timeTagColor: this.props.colorCodeTags ? 
                    getDeadlineTagColor(moment(this.props.meeting.time).diff(moment(), 'days')+1) :
                    "#108ee9"
        };
    }

    componentDidUpdate (prevprops) {
        if (this.props.meeting !== prevprops.meeting) {
            this.setState({
                meeting: this.props.meeting,
                timeTagColor: this.props.colorCodeTags ? 
                    getDeadlineTagColor(moment(this.props.meeting.time).diff(moment(), 'days')+1) :
                    "#108ee9"
            });
            this.updateDeadlineTagColor();
        }
        console.log(this.state);
    }

    updateDeadlineTagColor = () => {
        if(this.state.meeting.time) {
            this.setState({
                timeTagColor: this.props.colorCodeTags ? 
                    getDeadlineTagColor(moment(this.state.meeting.time).diff(moment(), 'days')+1) :
                    "#108ee9"
            });
        }
    }


    handleClick = () => {
        this.setState({visible:true});
    }

    handleCreate = async (value) => {
        let updatedMeeting = Object.assign({}, this.state.meeting, {
            title: value.title,
            time: value.time.format()
        });

        this.setState({
            meeting: updatedMeeting,
            visible: false,
        });

        this.updateDeadlineTagColor();

        try {
        const response = await 
            this.updateMeeting(value);
        } catch(err) {
            this.editErrorNotification(err);
            return
        }

        this.props.onChange();
        this.editSuccessNotification();
    }

    updateMeeting = async (value) => {
        return axios.post(`group/${this.state.meeting.group}/meetings/${this.state.meeting.id}/update`, {
            title: value.title,
            time: value.time.format()
        });
    }

    handleCancel = () => {
        this.setState({visible:false});
    }

    editSuccessNotification = () => {
        notification.success({
            message: 'Meeting Successfully edited!',
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
                title={this.state.meeting.title} 
                style={{ width: 250, display: 'inline-block', marginLeft: 10, marginBottom: 10 }}
                hoverable={true}
                onClick={ this.handleClick }
                >
                <Tag color={this.state.timeTagColor}>{moment(this.state.meeting.time).format('DD MMMM YYYY')}</Tag>
            </Card>

            <MeetingView
                visible={this.state.visible}
                onCreate={this.handleCreate}
                onCancel={this.handleCancel}
                meeting={this.state.meeting}
            />
            </div>
      );
    }
};

export default MeetingCard;