import React, { Component } from 'react';

import axios from 'axios';
import moment from 'moment';

import WelcomeMessage from '../components/WelcomeMessage';
import TaskCardList from '../components/TaskCardList';

import { Typography, Form, Button, Input, Checkbox, TimePicker, Divider, notification} from 'antd';
const { Title, Paragraph, Text } = Typography;

class SettingsPage extends Component {

    // Used to retrieve and manipulate the Antd FormInstance.
    formRef = React.createRef();

    constructor (props) {
        super(props);
        this.state = {
            settings: null,
        }
    }

    componentDidMount = () => {
        // When the component is mounted, fetch data from the backend API.
        axios.get(`${this.props.user_id}/settings`)
            .then(response => {

                // NOTE: The timedelta objects needs special formatting.
                this.setState({
                    settings:{...response.data,
                    defaultMeetingReminderTimedelta: moment(response.data.defaultMeetingReminderTimedelta, 'HH:mm'),
                    defaultTaskReminderTimedelta: moment(response.data.defaultTaskReminderTimedelta, 'HH:mm')}
                });

                // The antd form needs to be manually updated when setState is triggered.
                this.formRef.current.resetFields();
            })
            .catch(error => {
                alert(error);
                this.openErrorNotification();
                alert(axios.defaults.headers.common['token']);
            });
    }
    
    // When form input is valid and the user hits Save, update the data 
    // on the component state and push changes to backend using the HTTP PATCH method.
    onFinish = values => {
        this.setState({
            settings: {...values}
        });

        // NOTE: The timedelta objects needs special formatting.
        // TODO: Remove hardcoded user id.
        axios.patch(`${this.props.user_id}/settings`, {
            ...this.state.settings, 
            defaultMeetingReminderTimedelta: this.state.settings.defaultMeetingReminderTimedelta.format('HH:mm:ss'),
            defaultTaskReminderTimedelta: this.state.settings.defaultTaskReminderTimedelta.format('HH:mm:ss')
        }).then(() => {
            this.openSavedNotification();
        }).catch(() => {
            this.openErrorNotification();
        });
    };

    openSavedNotification = () => {
        notification.success({
          message: 'Settings saved!',
          duration: 2.5,
          style: {backgroundColor: '#efffcc'}
        });
    };

    openErrorNotification = () => {
        notification.error({
          message: 'Something went wrong!',
          duration: 4,
          style: {backgroundColor: '#ffcccb'}
        });
    };
    
    render () {
    return (
        <div className="page" style={{minHeight: '95vh'}}>
            
            <Typography>
            <Title>Settings</Title>
            </Typography>
            <Divider />
            
            <Form
                ref={this.formRef}
                onFinish={this.onFinish}
                initialValues={{
                    ...this.state.settings
                }}
            >
                    <Form.Item
                        name="autoCreateMeetingReminder"
                        valuePropName="checked"
                    >
                        <Checkbox>Automatically create reminders for meetings</Checkbox>
                    </Form.Item>
                    <Form.Item
                        label="Time before reminder is triggered"
                        name="defaultMeetingReminderTimedelta"
                        valuePropName="value"
                    >
                        
                        <TimePicker 
                            placeholder='hrs & mins'
                            format='HH:mm'
                            minuteStep={5}
                            showNow={false}
                            allowClear={false}
                        />
                        
                    </Form.Item>
                    <Form.Item
                        name="autoCreateTaskReminder"
                        valuePropName="checked"
                    >
                        <Checkbox>Automatically create reminders for tasks</Checkbox>
                    </Form.Item>
                    <Form.Item
                        label="Time before reminder is triggered"
                        name="defaultTaskReminderTimedelta"
                        valuePropName="value"
                    >
                        <TimePicker 
                            placeholder='hrs & mins'
                            format='HH:mm'
                            minuteStep={5}
                            showNow={false}
                            allowClear={false}
                        />
                    </Form.Item>

                    <Divider />

                    <Typography>
                    <Title level={3}>Push notifications</Title>
                    </Typography>

                    <Form.Item
                        name="pushNotifications"
                        valuePropName="checked"
                    >
                        <Checkbox>Send push notifications</Checkbox>
                    </Form.Item>

                    <Divider />

                    <Typography>
                    <Title level={3}>Bot settings</Title>
                    </Typography>

                    <Form.Item
                        name="botDetailedViewOnDefault"
                        valuePropName="checked"
                    >
                        <Checkbox>Display /tasklist in detailed view by default </Checkbox>
                    </Form.Item>
                    <Form.Item>
                        <Button type="primary" htmlType="submit">
                        Save
                        </Button>
                    </Form.Item>
            </Form>
        </div>
    );
    }
}

export default SettingsPage;