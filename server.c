#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>

#define PORT 8080
#define BUFFER_SIZE 1024
#define MAX_CLIENTS 100

typedef struct {
    int socket;
    int id;
    char ip[INET_ADDRSTRLEN];
} Client;

Client clients[MAX_CLIENTS];


int client_count = 0;
pthread_mutex_t client_mutex;
int next_client_id = 1;

void clear_terminal() {
    system("clear");
}

void print_connected_clients() {
    clear_terminal();
    pthread_mutex_lock(&client_mutex);
    printf("List of connected clients:\n");
    for (int i = 0; i < client_count; i++) {
        printf("ID: %d, IP: %s, Socket: %d\n", clients[i].id, clients[i].ip, clients[i].socket);
    }
    printf("\n");
    pthread_mutex_unlock(&client_mutex);
}

void send_command_to_all_clients(char *command) {
    pthread_mutex_lock(&client_mutex);
    for (int i = 0; i < client_count; i++) {
        write(clients[i].socket, command, strlen(command));
    }
    pthread_mutex_unlock(&client_mutex);
}

void send_command_to_selected_clients(char **selected_clients_ids, int selected_clients_count, char *command) {
    pthread_mutex_lock(&client_mutex);
    for (int i = 0; i < selected_clients_count; i++) {
        int selected_id = atoi(selected_clients_ids[i]);
        for (int j = 0; j < client_count; j++) {
            if (clients[j].id == selected_id) {
                write(clients[j].socket, command, strlen(command));
                break;
            }
        }
    }
    pthread_mutex_unlock(&client_mutex);
}

void *handle_client(void *socket_desc) {
    int sock = *(int*)socket_desc;
    struct sockaddr_in addr;
    socklen_t addr_size = sizeof(struct sockaddr_in);
    int res = getpeername(sock, (struct sockaddr*)&addr, &addr_size);

    char client_ip[INET_ADDRSTRLEN];
    if (res == 0) {
        inet_ntop(AF_INET, &(addr.sin_addr), client_ip, INET_ADDRSTRLEN);
    } else {
        perror("getpeername failed");
        strcpy(client_ip, "unknown");
    }

    pthread_mutex_lock(&client_mutex);

    // Sprawdzenie, czy klient o tym IP jest już podłączony
    for (int i = 0; i < client_count; i++) {
        if (strcmp(clients[i].ip, client_ip) == 0) {
            const char* message = "The client with the given IP is already connected\n";
            write(sock, message, strlen(message));  // Wysłanie komunikatu do klienta

            printf("Attempting to connect a client with IP: %s, which is already connected\n", client_ip);
            pthread_mutex_unlock(&client_mutex);
            close(sock);
            free(socket_desc);
            return NULL; // Zakończenie wątku
        }
    }

    int client_id = next_client_id++;
    clients[client_count].id = client_id;
    clients[client_count].socket = sock;
    strcpy(clients[client_count].ip, client_ip); 
    client_count++;

    pthread_mutex_unlock(&client_mutex);

    printf("Client with IP address: %s and ID: %d has connected\n", client_ip, client_id);

    clear_terminal();
    print_connected_clients();

    int read_size;
    char client_message[BUFFER_SIZE];

    while ((read_size = recv(sock, client_message, BUFFER_SIZE, 0)) > 0) {
        write(sock, client_message, strlen(client_message));
    }

    if (read_size == 0) {
        printf("Client with IP address: %s and ID: %d has disconnected\n", client_ip, client_id);
        pthread_mutex_lock(&client_mutex);
        for (int i = 0; i < client_count; i++) {
            if (clients[i].id == client_id) {
                for (int j = i; j < client_count - 1; j++) {
                    clients[j] = clients[j + 1];
                }
                client_count--;
                break;
            }
        }
        pthread_mutex_unlock(&client_mutex);
        fflush(stdout);

        clear_terminal();
        print_connected_clients();
    } else if (read_size == -1) {
        perror("recv failed");
    }

    close(sock);
    free(socket_desc);
    return 0;
}

void *handle_server_input(void *arg) {
    char command[BUFFER_SIZE];
    char client_id[100];

    while (1) {
        printf("Press Enter to enter command mode\n");
        getchar();  // Wait for Enter key

        clear_terminal();
        print_connected_clients();

        printf("Enter client IDs (comma-separated) and command: ");

        // Wczytaj całą linię komendy
        if (fgets(command, sizeof(command), stdin) == NULL) {
            perror("fgets failed");
            exit(EXIT_FAILURE);
        }

        // Podziel linię na identyfikatory klientów i komendę
        if (sscanf(command, "%s %[^\n]", client_id, command) != 2) {
            printf("Invalid input format\n");
            continue;
        }

        char *selected_clients_ids[MAX_CLIENTS];

        if (strcmp(client_id, "0") == 0) {
            for (int i = 0; i < client_count; i++) {
                char id_str[4];  // Załóżmy, że identyfikatory są liczby całkowite, co najwyżej 10 cyfr
                sprintf(id_str, "%d", clients[i].id);
                selected_clients_ids[i] = strdup(id_str);
            }

            send_command_to_selected_clients(selected_clients_ids, client_count, command);

            // Zwolnienie pamięci używanej do przechowywania identyfikatorów w postaci stringów
            for (int i = 0; i < client_count; i++) {
                free(selected_clients_ids[i]);
            }
            
        } else {
            char *token = strtok(client_id, ",");
            int selected_clients_count = 0;
            
            while (token != NULL) {
                selected_clients_ids[selected_clients_count++] = token;
                token = strtok(NULL, ",");
            }

            send_command_to_selected_clients(selected_clients_ids, selected_clients_count, command);
        }
    }
}

int main() {
    int server_fd, client_sock, c;
    struct sockaddr_in server, client;
    int *new_sock;

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1) {
        printf("Unable to create socket\n");
        return 1;
    }
    puts("Socket created");

    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }

    server.sin_family = AF_INET;
    server.sin_addr.s_addr = INADDR_ANY;
    server.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&server, sizeof(server)) < 0) {
        perror("bind failed");
        return 1;
    }
    puts("bind done");

    listen(server_fd, 3);

    pthread_t input_thread;
    memset(clients, 0, sizeof(clients));
    if (pthread_create(&input_thread, NULL, handle_server_input, NULL) < 0) {
        perror("could not create server input thread");
        return 1;
    }

    puts("Waiting for calls...");
    c = sizeof(struct sockaddr_in);
    while ((client_sock = accept(server_fd, (struct sockaddr *)&client, (socklen_t*)&c))) {
        puts("Connection accepted");

        pthread_t client_thread;
        new_sock = malloc(sizeof(int));
        if (new_sock == NULL) {
            perror("malloc failed");
            return 1;
        }
        *new_sock = client_sock;

        if (pthread_create(&client_thread, NULL, handle_client, (void*)new_sock) < 0) {
            perror("could not create thread");
            return 1;
        }

        puts("Handler assigned");
    }

    if (client_sock < 0) {
        perror("accept failed");
        return 1;
    }

    pthread_mutex_destroy(&client_mutex);
    return 0;
}
