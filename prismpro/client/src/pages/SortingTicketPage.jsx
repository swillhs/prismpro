import React, { Component } from 'react';
import {
  Table,
  Sorter
} from 'prism-reactjs';

const columns = [
  {
    title: 'Source Entity Name',
    id: 'source_entity_name'
  },
  {
    title: 'Source Entity UUID',
    id: 'source_entity_uuid'
  },
  {
    title: 'Alert Name',
    id: 'alert_name'
  },
  {
    title: 'Alert UUID',
    id: 'alert_uuid'
  },
  {
    title: 'Creation Time',
    id: 'creation_time'
  },
  {
    title: 'Severity',
    id: 'severity'
  }
];


const data = [];
for (let i = 0; i < 100; i++) {
  data.push({
    id: i,
    source_entity_name: `source_entity_name${i}`,
    source_entity_uuid: 'source_entity_uuid',
    alert_name:'alert_name',
    alert_uuid:'alert_uuid',
    creation_time:'creation_time',
    severity : 'severity'
  });
}

class SortingTicketPage extends Component {

  constructor(props) {
    super(props);

    this.state = {
      dataSource: data,
      loading: false,
      pagination: {
        total: 100,
        pageSize: 10,
        currentPage: 1,
        pageSizeOptions: [5, 10, 15]
      },
      sort: {
        order: Sorter.SORT_ORDER_CONST.ASCEND,
        column: 'source_entity_name',
        sortable: ['source_entity_name',
          'source_entity_uuid',
          'alert_name',
          'alert_uuid',
          'creation_time',
          'severity'
        ]
      }
    };
    this.handleChangePagination = this.handleChangePagination.bind(this);
    this.handleChangeSort = this.handleChangeSort.bind(this);
  }

  componentDidMount() {
    // axios
    //     .get("http://localhost:3000/ticket", {})
    //     .then(res => {
    //         for (var prop in res.data.tickets) {
    //             console.log(res.data.tickets[prop])
    //             data.push({
    //                 id: parseInt(prop),
    //                 source_entity_name: res.data.tickets[prop].source_entity_name,
    //                 source_entity_uuid: res.data.tickets[prop].source_entity_uuid,
    //                 alert_name: res.data.tickets[prop].alert_name,
    //                 alert_uuid: res.data.tickets[prop].alert_uuid,
    //                 creation_time: res.data.tickets[prop].creation_time,
    //                 severity: res.data.tickets[prop].severity
    //             });

    //         }
    //     })

  }

  render() {
    const {
      loading,
      pagination,
      sort
    } = this.state;

    const topSection = {
      title: 'Ticketing System',
      leftContent: <div>Left content</div>,
      rightContent: <div>Right content</div>
    };

    return (
      <Table
        oldTable={ false }
        columnKey="id"
        columns={ columns }
        dataSource={ this.getData(pagination, sort) }
        loading={ loading }
        pagination={ pagination }
        rowKey="id"
        sort={ sort }
        structure={ {
          paginationPosition: {
            top: true,
            bottom: true
          }
        } }
        onChangePagination={ this.handleChangePagination }
        onChangeSort={ this.handleChangeSort }
        topSection={ topSection }
      />
    );
  }

  getData(pagination, sort) {
    let newData = data.slice(0);

    // Sort logic
    newData.sort((a, b) => {
      const sortOrder = sort.order;
      let result;

      switch (this.state.sort.column) {
        case 'source_entity_name':
          result = a.source_entity_name.localeCompare(b.source_entity_name);
          break;
        case 'source_entity_uuid':
          result = a.source_entity_uuid.localeCompare(b.source_entity_uuid);
          break;
        case 'alert_name':
          result = a.alert_name.localeCompare(b.alert_name);
          break;
        case 'alert_uuid':
          result = a.alert_uuid.localeCompare(b.alert_uuid);
          break;
        case 'creation_time':
          result = a.creation_time.localeCompare(b.creation_time);
          break;
        case 'severity':
          result = a.severity.localeCompare(b.severity);
          break;
        default:
          break;
      }
      if (result !== 0) {
        return (sortOrder === Sorter.SORT_ORDER_CONST.DESCEND) ? -result : result;
      }
      return 0;
    });

    // Pagination logic
    const startIndex = (pagination.currentPage - 1) * pagination.pageSize;
    const endIndex = startIndex + pagination.pageSize;
    newData = newData.slice(startIndex, endIndex);

    return newData;
  }

  fetchData(pagination, sort) {
    this.setState({ loading: true });
    setTimeout(() => {
      const newState = {};

      newState.loading = false;
      newState.pagination = pagination || this.state.pagination;
      newState.sort = sort || this.state.sort;
      newState.dataSource = this.getData(newState.pagination, newState.sort);

      this.setState(newState);
    }, 2000);
  }

  handleChangePagination(pagination) {
    this.fetchData(pagination, null);
  }

  handleChangeSort(sort) {
    this.fetchData(null, sort);
  }


}

export default SortingTicketPage;
