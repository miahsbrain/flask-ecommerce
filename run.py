from project.main import create_app
main_app = create_app()

if __name__ == '__main__':
    main_app.run(host='0.0.0.0', port=5000, debug=True)