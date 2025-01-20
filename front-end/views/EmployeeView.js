import React, { useEffect, useState } from 'react';

const EmployeeView = () => {
    // State variable to show whether we're loading data or not.
    const [isLoading, setIsLoading] = useState(true);
    // State variable where we'll save our list of employees.
    const [employees, setEmployees] = useState([]);

    // This effect will be called when the component mounts and fetch the data
    // from our API using the fetch API.
    useEffect(() => {
        fetch(URLS.LIST_EMPLOYEES)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Check if data.results is defined and is an array
                const employeeList = Array.isArray(data) ? data : [];                setEmployees(employeeList);
                setIsLoading(false);
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                setIsLoading(false);
            });
    }, []);

    // Show a loading state if we haven't gotten data back yet.
    if (isLoading) {
        return <p>Employee data is loading...</p>;
    }

    // Show an "empty" state if we have no employees.
    if (employees.length === 0) {
        return <p>No employees found!</p>;
    } else {
        // Show our employee list component with the data we got back.
        return <EmployeeList employees={employees} />;
    }
}

const EmployeeList = (props) => {
    // This component renders a table of employees.
    return (
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Department</th>
                    <th>Salary</th>
                </tr>
            </thead>
            <tbody>
                {props.employees.map((employee, index) => (
                    <tr key={index}>
                        <td>{employee.name}</td>
                        <td>{employee.department}</td>
                        <td>{employee.salary}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

export default EmployeeView;
