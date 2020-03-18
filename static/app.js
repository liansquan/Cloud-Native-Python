function User(data) {
    this.id = ko.observable(data.id);
    this.name = ko.observable(data.name);
    this.username = ko.observable(data.username);
    this.email = ko.observable(data.email);
    this.password = ko.observable(data.password);
}

