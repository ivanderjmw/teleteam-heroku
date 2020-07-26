import React, { useState } from 'react';
import moment from 'moment';
import { notification, Button, Modal, Form, Input, DatePicker, TimePicker, Select, Space } from 'antd';
import axios from 'axios';

const CreateMeetingForm = ({ visible, onCreate, onCancel, group_id }) => {
  const { Option } = Select;

  const [form] = Form.useForm();

  const today = moment()

  return (
    <Modal
      visible={visible}
      title="Create a new Meeting"
      okText="Create"
      cancelText="Cancel"
      onCancel={onCancel}
      onOk={() => {
        form
          .validateFields()
          .then(values => {
            form.resetFields();
            onCreate(values);
          })
          .catch(info => {
            console.log('Validate Failed:', info);
          });
      }}
    >
      <Form
        form={form}
        layout="vertical"
        name="form_in_modal"
        initialValues={{
          modifier: 'public',
        }}
      >
        <Form.Item
          name="title"
          label="Title"
          rules={[
            {
              required: true,
              message: 'Please input the title of collection!',
            },
          ]}
        >
          <Input />
        </Form.Item>
        <Space>
            <Form.Item 
              name="date" 
              className="Date"
              label="Due Date"
              rules={[
                  {
                    required: true,
                    message: 'Please input the date of the Task!',
                  },
                ]}
              initialValue={today}
              >
                  <DatePicker format="YYYY-MM-DD" />
            </Form.Item>
            <Form.Item 
              name="time" 
              className="Time" 
              label="Due Time"
              initialValue={today}
            >
                  <TimePicker format="HH:mm" minuteStep={10}/>
            </Form.Item>
            <Form.Item name="timezone" className="Timezone" label="Time Zone" initialValue="+08:00">
                  <Select 
                    style={{ width: '100%' }}
                    mode="single"
                    placeholder="Select Timezone.."                    
                  >
                    <Option value="+07:00">GMT+7 - Jakarta</Option>
                    <Option value="+08:00">GMT+8 - Singapore</Option>
                  </Select>
            </Form.Item>
          </Space>
      </Form>
    </Modal>
  );
};

const CreateMeetingButton = ({members, group_id, onCreateMeetingUpdate}) => {
  const [visible, setVisible] = useState(false);

  const createSuccessNotification = () => {
    notification.success({
        message: 'Meeting Successfully created!',
        duration: 2.5,
        style: {backgroundColor: '#efffcc'}
      });
  };

  const createErrorNotification = (err) => {
      notification.error({
        message: `Something went wrong! ${err}`,
        duration: 4,
        style: {backgroundColor: '#ffcccb'}
      });
  };

  const onCreate = value => {
    console.log('Received values of form: ', value);
    let newMeeting = {
      title: value.title,
      // TODO: implement time zones
      time: value.date.format('YYYY-MM-DD')+'T'+value.time.format('HH:mm:ss')+value.timezone
    };

    console.log(newMeeting);

    axios.post(
      `group/${group_id}/meetings/create`,
      newMeeting
    ).then(res => {onCreateMeetingUpdate(res.data); createSuccessNotification();})
    .catch(err => createErrorNotification(err));
    setVisible(false);
  };

  return (
    <div>
      <Button
        type="primary"
        onClick={() => {
          setVisible(true);
        }}
      >
        New Meeting
      </Button>
      <CreateMeetingForm
        visible={visible}
        onCreate={onCreate}
        onCancel={() => {
          setVisible(false);
        }}
        members={members}
        group_id={group_id}
      />
    </div>
  );
};

const CreateTaskForm = ({ visible, onCreate, onCancel, members, group_id }) => {

    const { Option } = Select;

    const [form] = Form.useForm();

    const member_options = (members) => {
      try {
          return members.map(user => { return (<Option value={user.username}>{user.username}</Option>)});
      } catch (error) {
          return null;
      }
    }

    const today = moment()

    return (
      <Modal
        visible={visible}
        title="Create a new Task"
        okText="Create"
        cancelText="Cancel"
        onCancel={onCancel}
        onOk={() => {
          form
            .validateFields()
            .then(values => {
              form.resetFields();
              onCreate(values);
            })
            .catch(info => {
              console.log('Validate Failed:', info);
            });
        }}
      >
        <Form
          form={form}
          layout="vertical"
          name="form_in_modal"
          initialValues={{
            modifier: 'public',
          }}
        >
          <Form.Item
            name="title"
            label="Title"
            rules={[
              {
                required: true,
                message: 'Please input the title of collection!',
              },
            ]}
          >
            <Input />
          </Form.Item>
          <Space>
            <Form.Item 
              name="date" 
              className="Date"
              label="Due Date"
              rules={[
                  {
                    required: true,
                    message: 'Please input the date of the Task!',
                  },
                ]}
              initialValue={today}
              >
                  <DatePicker format="YYYY-MM-DD" />
            </Form.Item>
            <Form.Item 
              name="time" 
              className="Time" 
              label="Due Time"
              initialValue={today}
            >
                  <TimePicker format="HH:mm" minuteStep={10}/>
            </Form.Item>
            <Form.Item name="timezone" className="Timezone" label="Time Zone" initialValue="+08:00">
                  <Select 
                    style={{ width: '100%' }}
                    mode="single"
                    placeholder="Select Timezone.."                    
                  >
                    <Option value="+07:00">GMT+7 - Jakarta</Option>
                    <Option value="+08:00">GMT+8 - Singapore</Option>
                  </Select>
            </Form.Item>
          </Space>
          <Form.Item name="assignedUsers" className="Assigned-Users" label="Assigned Users"
            rules={[
              {
                required: true,
                message: 'Please input at least one assigned Users!',
              },
            ]}
          >
            <Select
                mode="multiple"
                style={{ width: '100%' }}
                placeholder="Please select"
                defaultValue={[]}
            >
                { member_options(members) }
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    );
  };
  
  const CreateTaskButton = ({members, group_id, onCreateTaskUpdate}) => {
    const [visible, setVisible] = useState(false);
    
    const createSuccessNotification = () => {
      notification.success({
          message: 'Task Successfully created!',
          duration: 2.5,
          style: {backgroundColor: '#efffcc'}
        });
    };

    const createErrorNotification = (err) => {
        notification.error({
          message: `Something went wrong! ${err}`,
          duration: 4,
          style: {backgroundColor: '#ffcccb'}
        });
    };


    const onCreate = value => {
      console.log('Received values of form: ', value);
      let newTask = {
        title: value.title,
        // TODO: implement time zones
        deadline: value.date.format('YYYY-MM-DD')+'T'+value.time.format('HH:mm:ss')+value.timezone,
        done: false,
        assigned_users: value.assignedUsers.map(username => 
            members.find((user) => user.username === username).id)
      };

      console.log(newTask);

      axios.post(
        `group/${group_id}/tasks/create`,
        newTask
      ).then(res => {onCreateTaskUpdate(res.data); createSuccessNotification();})
      .catch(err => createErrorNotification(err));
      setVisible(false);
    };


  
    return (
      <div>
        <Button
          type="primary"
          onClick={() => {
            setVisible(true);
          }}
        >
          New Task
        </Button>
        <CreateTaskForm
          visible={visible}
          onCreate={onCreate}
          onCancel={() => {
            setVisible(false);
          }}
          members={members}
          group_id={group_id}
        />
      </div>
    );
  };
  



export { CreateMeetingButton, CreateTaskButton };