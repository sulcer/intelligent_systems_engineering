import React, {FC} from 'react';

interface TableProps {
    rows: any[];
}

const Table:FC<TableProps> = ({ rows }) => {
    return (
        <div className="overflow-x-auto mt-5">
            <p className={'font-semibold'}>Predictions:</p>
            <p className={'text-sm text-gray-500'}>*in time units (hours)</p>
            <table className="table-auto border-collapse border">
                <thead>
                <tr className="bg-gray-100">
                    <th className="px-4 py-2">ONE</th>
                    <th className="px-4 py-2">TWO</th>
                    <th className="px-4 py-2">THREE</th>
                    <th className="px-4 py-2">FOUR</th>
                    <th className="px-4 py-2">FIVE</th>
                    <th className="px-4 py-2">SIX</th>
                    <th className="px-4 py-2">SEVEN</th>
                </tr>
                </thead>
                <tbody>
                <tr className="bg-gray-50">
                    {rows?.map((value, index) => (
                        <td key={index} className="border px-4 py-2 text-center">{value}</td>
                    ))}
                </tr>
                </tbody>
            </table>
        </div>
    );
};

export default Table;