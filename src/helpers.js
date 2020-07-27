const getDeadlineTagColor = (daysLeft) => {
    if(daysLeft>5){
        return "#42DB3F";
    }else if(daysLeft>3){
        return "#E0E32D";
    }else{
        return "#E05A3D";
    }
};

function getLoginStatus () {
    try {
      return localStorage.getItem('logged_in') == 'true'
    } catch (error) {
      return false
    }
}

export {getDeadlineTagColor, getLoginStatus};